"""Tag and TaskTag entities for task categorization."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, UniqueConstraint


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_tag_user_name"),)

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, nullable=False)
    user_id: uuid.UUID = Field(nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks.id", primary_key=True, nullable=False)
    tag_id: int = Field(foreign_key="tags.id", primary_key=True, nullable=False)
