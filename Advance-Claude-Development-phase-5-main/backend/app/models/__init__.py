"""SQLModel entities — import all models so Alembic discovers them."""

from app.models.completion import CompletionRecord
from app.models.conversation import Conversation, Message, MessageRole
from app.models.reminder import Reminder, ReminderStatus
from app.models.tag import Tag, TaskTag
from app.models.task import (
    Task,
    TaskCreate,
    TaskPriority,
    TaskRead,
    TaskStatus,
    TaskUpdate,
)
from app.models.user import User

__all__ = [
    "CompletionRecord",
    "Conversation",
    "Message",
    "MessageRole",
    "Reminder",
    "ReminderStatus",
    "Tag",
    "Task",
    "TaskCreate",
    "TaskPriority",
    "TaskRead",
    "TaskStatus",
    "TaskTag",
    "TaskUpdate",
    "User",
]
