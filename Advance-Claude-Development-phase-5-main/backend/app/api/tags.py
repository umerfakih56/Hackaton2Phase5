"""Tag routes per contracts/backend-api.md."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_id, get_db
from app.services import tag_service

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get(
    "",
    summary="List tags",
    description=(
        "Retrieve all tags for the current user with task counts. "
        "Supports autocomplete filtering via the ?q= parameter."
    ),
)
async def list_tags(
    q: str | None = Query(None, description="Optional prefix filter for autocomplete"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    tags = await tag_service.list_tags(db, user_id, q=q)
    return {"tags": tags}
