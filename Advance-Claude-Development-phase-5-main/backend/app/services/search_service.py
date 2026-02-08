"""Search service — full-text search using PostgreSQL tsvector."""

import uuid

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task


async def search_tasks(
    db: AsyncSession,
    user_id: uuid.UUID,
    query: str,
    *,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Task], int]:
    """Full-text search across task titles and descriptions.

    Uses the search_vector tsvector column with plainto_tsquery.
    Falls back to ILIKE if the query is very short.
    """
    base = select(Task).where(Task.user_id == user_id)

    if len(query.strip()) >= 2:
        # Use tsvector search with ranking
        base = base.where(
            text("search_vector @@ plainto_tsquery('english', :q)").bindparams(q=query)
        ).order_by(
            text(
                "ts_rank(search_vector, plainto_tsquery('english', :q)) DESC"
            ).bindparams(q=query)
        )
    else:
        # Fallback: simple ILIKE for very short queries
        base = base.where(Task.title.ilike(f"%{query}%"))

    # Count
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Paginate
    base = base.offset(offset).limit(limit)
    result = await db.execute(base)

    return list(result.scalars().all()), total
