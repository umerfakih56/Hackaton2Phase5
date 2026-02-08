"""Tag service — CRUD operations and autocomplete."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag, TaskTag


async def list_tags(
    db: AsyncSession, user_id: uuid.UUID, q: str | None = None
) -> list[dict]:
    """List tags for a user with task counts, optionally filtered by prefix."""
    stmt = (
        select(Tag.id, Tag.name, func.count(TaskTag.task_id).label("task_count"))
        .outerjoin(TaskTag, TaskTag.tag_id == Tag.id)
        .where(Tag.user_id == user_id)
        .group_by(Tag.id, Tag.name)
        .order_by(Tag.name)
    )

    if q:
        stmt = stmt.where(Tag.name.ilike(f"{q}%"))

    result = await db.execute(stmt)
    return [
        {"id": row.id, "name": row.name, "task_count": row.task_count}
        for row in result.all()
    ]
