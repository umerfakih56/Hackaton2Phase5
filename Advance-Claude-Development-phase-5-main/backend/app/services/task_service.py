"""Task service — CRUD operations with priority, event publishing."""

import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.completion import CompletionRecord
from app.models.tag import Tag, TaskTag
from app.models.task import (
    Task,
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)
from app.services.event_publisher import publish_task_event

logger = structlog.get_logger()


def _validate_recurrence_pattern(pattern: dict) -> None:
    """Validate recurrence pattern JSONB per data-model.md rules.

    Raises ValueError on invalid patterns.
    """
    rtype = pattern.get("type")
    if rtype not in ("daily", "weekly", "monthly", "custom"):
        raise ValueError(f"Invalid recurrence type: {rtype}")

    if rtype == "weekly":
        days = pattern.get("days_of_week")
        if not days or not isinstance(days, list) or len(days) == 0:
            raise ValueError(
                "Weekly recurrence requires 'days_of_week' with at least one entry"
            )
        for d in days:
            if not isinstance(d, int) or d < 0 or d > 6:
                raise ValueError(f"Invalid day_of_week value: {d} (must be 0-6)")

    elif rtype == "monthly":
        day = pattern.get("day_of_month")
        if day is None or not isinstance(day, int) or day < 1 or day > 31:
            raise ValueError("Monthly recurrence requires 'day_of_month' (1-31)")

    elif rtype == "custom":
        interval = pattern.get("interval_days")
        if not interval or not isinstance(interval, int) or interval < 1:
            raise ValueError("Custom recurrence requires 'interval_days' >= 1")


def _task_to_read(task: Task, tags: list[str] | None = None) -> TaskRead:
    """Convert a Task ORM object to a TaskRead response schema."""
    return TaskRead(
        id=task.id,  # type: ignore[arg-type]
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        tags=tags or [],
        due_date=task.due_date,
        is_recurring=task.is_recurring,
        recurrence_pattern=task.recurrence_pattern,
        reminder_offset=task.reminder_offset,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


async def _get_tags_for_task(db: AsyncSession, task_id: int) -> list[str]:
    """Fetch tag names associated with a task."""
    stmt = (
        select(Tag.name)
        .join(TaskTag, TaskTag.tag_id == Tag.id)
        .where(TaskTag.task_id == task_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _sync_tags(
    db: AsyncSession, task_id: int, user_id: uuid.UUID, tag_names: list[str]
) -> list[str]:
    """Create-or-get tags by name and associate them with the task."""
    # Remove existing associations
    existing = (
        (await db.execute(select(TaskTag).where(TaskTag.task_id == task_id)))
        .scalars()
        .all()
    )
    for tt in existing:
        await db.delete(tt)

    if not tag_names:
        return []

    resolved: list[str] = []
    for name in tag_names:
        clean = name.strip().lower()
        if not clean:
            continue

        # Get or create tag
        stmt = select(Tag).where(Tag.name == clean, Tag.user_id == user_id)
        tag = (await db.execute(stmt)).scalar_one_or_none()
        if tag is None:
            tag = Tag(name=clean, user_id=user_id)
            db.add(tag)
            await db.flush()

        # Create junction row
        db.add(TaskTag(task_id=task_id, tag_id=tag.id))  # type: ignore[arg-type]
        resolved.append(clean)

    return resolved


async def create_task(
    db: AsyncSession, user_id: uuid.UUID, data: TaskCreate
) -> TaskRead:
    """Create a new task and publish a 'created' event."""
    # Validate recurrence pattern if recurring
    if data.is_recurring:
        if not data.recurrence_pattern:
            raise ValueError("Recurring tasks require a recurrence_pattern")
        _validate_recurrence_pattern(data.recurrence_pattern)

    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
        status=TaskStatus.PENDING,
        priority=data.priority or TaskPriority.MEDIUM,
        due_date=data.due_date,
        is_recurring=data.is_recurring,
        recurrence_pattern=data.recurrence_pattern,
        reminder_offset=data.reminder_offset,
    )
    db.add(task)
    await db.flush()

    # Sync tags
    tags = await _sync_tags(db, task.id, user_id, data.tags)  # type: ignore[arg-type]

    await db.commit()
    await db.refresh(task)

    read = _task_to_read(task, tags)

    # Fire-and-forget event
    await publish_task_event(
        event_type="created",
        task_id=task.id,  # type: ignore[arg-type]
        task_data=read.model_dump(mode="json"),
        user_id=str(user_id),
    )

    return read


async def get_task(
    db: AsyncSession, user_id: uuid.UUID, task_id: int
) -> TaskRead | None:
    """Get a single task by ID (scoped to user)."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await db.execute(stmt)).scalar_one_or_none()
    if task is None:
        return None

    tags = await _get_tags_for_task(db, task_id)
    return _task_to_read(task, tags)


async def list_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    tag_names: list[str] | None = None,
    due_from: datetime | None = None,
    due_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
    q: str | None = None,
) -> dict:
    """List tasks with filters, sorting, and pagination."""
    base = select(Task).where(Task.user_id == user_id)

    if status is not None:
        base = base.where(Task.status == status)
    if priority is not None:
        base = base.where(Task.priority == priority)
    if due_from is not None:
        base = base.where(Task.due_date >= due_from)
    if due_to is not None:
        base = base.where(Task.due_date <= due_to)
    if tag_names:
        for tag_name in tag_names:
            sub = (
                select(TaskTag.task_id)
                .join(Tag, Tag.id == TaskTag.tag_id)
                .where(Tag.name == tag_name.strip().lower(), Tag.user_id == user_id)
            )
            base = base.where(Task.id.in_(sub))
    if q:
        base = base.where(Task.title.ilike(f"%{q}%") | Task.description.ilike(f"%{q}%"))

    # Count total
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Sorting
    sort_col = getattr(Task, sort_by, Task.created_at)
    if sort_order == "asc":
        base = base.order_by(sort_col.asc())
    else:
        base = base.order_by(sort_col.desc())

    # Pagination
    offset = (page - 1) * page_size
    base = base.offset(offset).limit(page_size)

    result = await db.execute(base)
    tasks = result.scalars().all()

    reads = []
    for t in tasks:
        tags = await _get_tags_for_task(db, t.id)  # type: ignore[arg-type]
        reads.append(_task_to_read(t, tags))

    return {
        "tasks": [r.model_dump(mode="json") for r in reads],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def update_task(
    db: AsyncSession, user_id: uuid.UUID, task_id: int, data: TaskUpdate
) -> TaskRead | None:
    """Partially update a task and publish an 'updated' event."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await db.execute(stmt)).scalar_one_or_none()
    if task is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tags", None)

    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)

    if tag_names is not None:
        tags = await _sync_tags(db, task_id, user_id, tag_names)
    else:
        tags = await _get_tags_for_task(db, task_id)

    await db.commit()
    await db.refresh(task)

    read = _task_to_read(task, tags)

    await publish_task_event(
        event_type="updated",
        task_id=task_id,
        task_data=read.model_dump(mode="json"),
        user_id=str(user_id),
    )

    return read


async def complete_task(
    db: AsyncSession, user_id: uuid.UUID, task_id: int
) -> TaskRead | None:
    """Mark a task as completed and publish a 'completed' event."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await db.execute(stmt)).scalar_one_or_none()
    if task is None:
        return None

    if task.status == TaskStatus.COMPLETED:
        return None  # Already completed — caller should return 409

    now = datetime.now(timezone.utc)
    task.status = TaskStatus.COMPLETED
    task.completed_at = now
    task.updated_at = now

    # Create CompletionRecord for history tracking
    record = CompletionRecord(
        task_id=task_id,
        completed_at=now,
        completed_by=user_id,
    )
    db.add(record)

    await db.commit()
    await db.refresh(task)

    tags = await _get_tags_for_task(db, task_id)
    read = _task_to_read(task, tags)

    await publish_task_event(
        event_type="completed",
        task_id=task_id,
        task_data=read.model_dump(mode="json"),
        user_id=str(user_id),
    )

    return read


async def reopen_task(
    db: AsyncSession, user_id: uuid.UUID, task_id: int
) -> TaskRead | None:
    """Reopen a completed task."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await db.execute(stmt)).scalar_one_or_none()
    if task is None:
        return None

    if task.status != TaskStatus.COMPLETED:
        return None  # Not completed — caller should return 409

    task.status = TaskStatus.PENDING
    task.completed_at = None
    task.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(task)

    tags = await _get_tags_for_task(db, task_id)
    read = _task_to_read(task, tags)

    await publish_task_event(
        event_type="updated",
        task_id=task_id,
        task_data=read.model_dump(mode="json"),
        user_id=str(user_id),
    )

    return read


async def delete_task(db: AsyncSession, user_id: uuid.UUID, task_id: int) -> bool:
    """Delete a task and publish a 'deleted' event."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = (await db.execute(stmt)).scalar_one_or_none()
    if task is None:
        return False

    # Remove tag associations first
    tag_links = (
        (await db.execute(select(TaskTag).where(TaskTag.task_id == task_id)))
        .scalars()
        .all()
    )
    for link in tag_links:
        await db.delete(link)

    await db.delete(task)
    await db.commit()

    await publish_task_event(
        event_type="deleted",
        task_id=task_id,
        task_data={"id": task_id},
        user_id=str(user_id),
    )

    return True


async def get_dashboard_stats(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Get dashboard statistics for the authenticated user."""
    base = select(Task).where(Task.user_id == user_id)

    total = (
        await db.execute(select(func.count()).select_from(base.subquery()))
    ).scalar() or 0

    pending = (
        await db.execute(
            select(func.count()).select_from(
                base.where(Task.status == TaskStatus.PENDING).subquery()
            )
        )
    ).scalar() or 0

    completed = (
        await db.execute(
            select(func.count()).select_from(
                base.where(Task.status == TaskStatus.COMPLETED).subquery()
            )
        )
    ).scalar() or 0

    now = datetime.now(timezone.utc)
    overdue = (
        await db.execute(
            select(func.count()).select_from(
                base.where(
                    Task.status == TaskStatus.PENDING,
                    Task.due_date < now,
                    Task.due_date.isnot(None),
                ).subquery()
            )
        )
    ).scalar() or 0

    high_priority = (
        await db.execute(
            select(func.count()).select_from(
                base.where(
                    Task.status == TaskStatus.PENDING,
                    Task.priority == TaskPriority.HIGH,
                ).subquery()
            )
        )
    ).scalar() or 0

    return {
        "total": total,
        "pending": pending,
        "completed": completed,
        "overdue": overdue,
        "high_priority": high_priority,
    }
