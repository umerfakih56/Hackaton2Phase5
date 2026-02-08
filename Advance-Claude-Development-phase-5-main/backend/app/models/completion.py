"""CompletionRecord entity for recurring task history."""

import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class CompletionRecord(SQLModel, table=True):
    __tablename__ = "completion_records"

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", nullable=False, index=True)
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    completed_by: uuid.UUID = Field(nullable=False)
