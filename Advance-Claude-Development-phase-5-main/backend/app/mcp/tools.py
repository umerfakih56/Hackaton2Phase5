"""MCP tool definitions for the AI agent — task CRUD operations."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import TaskCreate, TaskPriority, TaskUpdate
from app.services import task_service


async def add_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
    due_date: str | None = None,
    reminder_offset: str | None = None,
    is_recurring: bool = False,
    recurrence_pattern: dict[str, Any] | None = None,
) -> dict:
    """Create a new task.

    Args:
        title: Task title (required).
        description: Optional longer description.
        priority: One of "high", "medium", "low". Defaults to "medium".
        tags: Optional list of tag names.
        due_date: Optional ISO 8601 datetime string.
        reminder_offset: Optional offset like "1h", "1d", "15m".
        is_recurring: Whether this task recurs.
        recurrence_pattern: JSONB recurrence config if is_recurring is True.
    """
    from datetime import datetime

    parsed_due = None
    if due_date:
        parsed_due = datetime.fromisoformat(due_date)

    data = TaskCreate(
        title=title,
        description=description,
        priority=TaskPriority(priority),
        tags=tags or [],
        due_date=parsed_due,
        reminder_offset=reminder_offset,
        is_recurring=is_recurring,
        recurrence_pattern=recurrence_pattern,
    )
    result = await task_service.create_task(db, user_id, data)
    return result.model_dump(mode="json")


async def update_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
    reminder_offset: str | None = None,
    is_recurring: bool | None = None,
    recurrence_pattern: dict[str, Any] | None = None,
) -> dict:
    """Update an existing task. Only include fields you want to change.

    Args:
        task_id: ID of the task to update (required).
        title: New title.
        description: New description.
        priority: New priority ("high", "medium", "low").
        tags: New list of tag names (replaces all existing tags).
        due_date: New due date (ISO 8601).
        reminder_offset: New reminder offset.
        is_recurring: Whether this task recurs.
        recurrence_pattern: New recurrence config.
    """
    from datetime import datetime

    parsed_due = None
    if due_date:
        parsed_due = datetime.fromisoformat(due_date)

    update_data: dict[str, Any] = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if priority is not None:
        update_data["priority"] = TaskPriority(priority)
    if tags is not None:
        update_data["tags"] = tags
    if due_date is not None:
        update_data["due_date"] = parsed_due
    if reminder_offset is not None:
        update_data["reminder_offset"] = reminder_offset
    if is_recurring is not None:
        update_data["is_recurring"] = is_recurring
    if recurrence_pattern is not None:
        update_data["recurrence_pattern"] = recurrence_pattern

    data = TaskUpdate(**update_data)
    result = await task_service.update_task(db, user_id, task_id, data)
    if result is None:
        return {"error": f"Task {task_id} not found"}
    return result.model_dump(mode="json")


async def complete_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    task_id: int,
) -> dict:
    """Mark a task as completed.

    Args:
        task_id: ID of the task to complete (required).
    """
    result = await task_service.complete_task(db, user_id, task_id)
    if result is None:
        return {"error": f"Task {task_id} not found or already completed"}
    return result.model_dump(mode="json")


async def delete_task(
    db: AsyncSession,
    user_id: uuid.UUID,
    task_id: int,
) -> dict:
    """Delete a task permanently.

    Args:
        task_id: ID of the task to delete (required).
    """
    deleted = await task_service.delete_task(db, user_id, task_id)
    if not deleted:
        return {"error": f"Task {task_id} not found"}
    return {"deleted": True, "task_id": task_id}


async def list_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    q: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List tasks with optional filtering and sorting.

    Args:
        q: Full-text search query.
        status: Filter by "pending" or "completed".
        priority: Filter by "high", "medium", or "low".
        tags: Filter by tag names (AND logic).
        sort_by: Sort field ("created_at", "due_date", "priority", "title").
        sort_order: "asc" or "desc".
        page: Page number (1-based).
        page_size: Items per page (max 100).
    """
    from app.models.task import TaskPriority as TP
    from app.models.task import TaskStatus as TS

    parsed_status = TS(status) if status else None
    parsed_priority = TP(priority) if priority else None

    return await task_service.list_tasks(
        db,
        user_id,
        status=parsed_status,
        priority=parsed_priority,
        tag_names=tags,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        q=q,
    )


# Tool registry for the agent to discover
TOOLS = {
    "add_task": add_task,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "list_tasks": list_tasks,
}
