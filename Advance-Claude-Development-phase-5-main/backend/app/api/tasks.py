"""Task CRUD routes per contracts/backend-api.md."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.models.completion import CompletionRecord
from app.models.task import (
    Task,
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post(
    "",
    status_code=201,
    response_model=TaskRead,
    summary="Create a task",
    description=(
        "Create a new task with optional tags, recurrence pattern, and reminder offset."
    ),
)
async def create_task(
    data: TaskCreate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await task_service.create_task(db, user_id, data)


@router.get(
    "",
    summary="List tasks",
    description=(
        "Retrieve paginated tasks with optional filters "
        "for status, priority, tags, due date range, "
        "full-text search, and sorting."
    ),
)
async def list_tasks(
    q: str | None = Query(None),
    status: TaskStatus | None = Query(None),
    priority: TaskPriority | None = Query(None),
    tags: list[str] | None = Query(None),
    due_from: datetime | None = Query(None),
    due_to: datetime | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await task_service.list_tasks(
        db,
        user_id,
        status=status,
        priority=priority,
        tag_names=tags,
        due_from=due_from,
        due_to=due_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        q=q,
    )


@router.get(
    "/dashboard",
    summary="Dashboard statistics",
    description=(
        "Returns aggregate counts: total, pending, "
        "completed, overdue, and high-priority tasks."
    ),
)
async def dashboard_stats(
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    return await task_service.get_dashboard_stats(db, user_id)


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a task",
    description=(
        "Retrieve a single task by ID. "
        "Returns 404 if not found or not owned by the user."
    ),
)
async def get_task(
    task_id: int,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    task = await task_service.get_task(db, user_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description=(
        "Partially update a task. Only provided fields "
        "are changed. Publishes a task.updated event."
    ),
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    task = await task_service.update_task(db, user_id, task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post(
    "/{task_id}/complete",
    response_model=TaskRead,
    summary="Complete a task",
    description=(
        "Mark a task as completed. Creates a CompletionRecord "
        "for recurring tasks. Returns 409 if already completed."
    ),
)
async def complete_task(
    task_id: int,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await task_service.complete_task(db, user_id, task_id)
    if result is None:
        # Distinguish between not found and already completed
        existing = await task_service.get_task(db, user_id, task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=409, detail="Task already completed")
    return result


@router.post(
    "/{task_id}/reopen",
    response_model=TaskRead,
    summary="Reopen a task",
    description=(
        "Reopen a previously completed task. "
        "Returns 409 if the task is not in completed status."
    ),
)
async def reopen_task(
    task_id: int,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    result = await task_service.reopen_task(db, user_id, task_id)
    if result is None:
        existing = await task_service.get_task(db, user_id, task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=409, detail="Task is not completed")
    return result


@router.delete(
    "/{task_id}",
    status_code=204,
    summary="Delete a task",
    description=(
        "Permanently delete a task and its associated "
        "tags, reminders, and completion records."
    ),
)
async def delete_task(
    task_id: int,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    deleted = await task_service.delete_task(db, user_id, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get(
    "/{task_id}/completions",
    summary="Get completion history",
    description=(
        "Retrieve the completion history for a recurring "
        "task, ordered by most recent first."
    ),
)
async def get_completions(
    task_id: int,
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get completion history for a recurring task."""
    # Verify task ownership
    task = (
        await db.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
    ).scalar_one_or_none()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    records = (
        (
            await db.execute(
                select(CompletionRecord)
                .where(CompletionRecord.task_id == task_id)
                .order_by(CompletionRecord.completed_at.desc())
            )
        )
        .scalars()
        .all()
    )

    return {
        "completions": [
            {
                "id": r.id,
                "completed_at": r.completed_at.isoformat(),
                "completed_by": str(r.completed_by),
            }
            for r in records
        ]
    }
