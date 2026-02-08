"""Task entity — core unit of work with priority, tags, recurrence."""

import enum
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, SQLModel, String


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, sa_column=Column(Text))
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        sa_column=Column(String(10), nullable=False, default="medium", index=True),
    )
    due_date: datetime | None = Field(default=None, index=True)
    is_recurring: bool = Field(default=False)
    recurrence_pattern: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB, nullable=True)
    )
    reminder_offset: str | None = Field(default=None, max_length=50)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    completed_at: datetime | None = Field(default=None)


class TaskCreate(SQLModel):
    """Schema for creating a task."""

    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    tags: list[str] = []
    due_date: datetime | None = None
    reminder_offset: str | None = None
    is_recurring: bool = False
    recurrence_pattern: dict[str, Any] | None = None


class TaskUpdate(SQLModel):
    """Schema for partial task update."""

    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    tags: list[str] | None = None
    due_date: datetime | None = None
    reminder_offset: str | None = None
    is_recurring: bool | None = None
    recurrence_pattern: dict[str, Any] | None = None


class TaskRead(SQLModel):
    """Schema for task response."""

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    tags: list[str] = []
    due_date: datetime | None
    is_recurring: bool
    recurrence_pattern: dict[str, Any] | None
    reminder_offset: str | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
