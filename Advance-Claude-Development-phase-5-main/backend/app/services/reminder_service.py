"""Reminder service — create, cancel, compute remind_at from due_date + offset."""

import re
import uuid
from datetime import datetime, timedelta, timezone

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder, ReminderStatus
from app.services.event_publisher import publish_reminder_event

logger = structlog.get_logger()

# Offset patterns: "15m", "1h", "1d", "2h30m", etc.
OFFSET_PATTERN = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?")


def parse_offset(offset_str: str) -> timedelta:
    """Parse a reminder offset string like '1h', '1d', '30m' into a timedelta."""
    m = OFFSET_PATTERN.fullmatch(offset_str.strip())
    if not m or not any(m.groups()):
        raise ValueError(f"Invalid reminder offset format: {offset_str}")

    days = int(m.group(1) or 0)
    hours = int(m.group(2) or 0)
    minutes = int(m.group(3) or 0)
    return timedelta(days=days, hours=hours, minutes=minutes)


def compute_remind_at(due_date: datetime, offset_str: str) -> datetime:
    """Compute the reminder trigger time by subtracting offset from due_date."""
    delta = parse_offset(offset_str)
    return due_date - delta


async def create_reminder(
    db: AsyncSession,
    task_id: int,
    user_id: uuid.UUID,
    due_date: datetime,
    offset_str: str,
) -> Reminder:
    """Create a reminder for a task and publish a ReminderEvent."""
    remind_at = compute_remind_at(due_date, offset_str)
    job_name = f"reminder-task-{task_id}"

    # Cancel existing reminder for this task if any
    await cancel_reminder(db, task_id)

    reminder = Reminder(
        task_id=task_id,
        user_id=user_id,
        remind_at=remind_at,
        status=ReminderStatus.PENDING,
        job_name=job_name,
    )
    db.add(reminder)
    await db.flush()

    # Publish reminder event for the notification service
    await publish_reminder_event(
        task_id=task_id,
        title="",  # Will be populated by the caller
        due_at=due_date.isoformat(),
        remind_at=remind_at.isoformat(),
        user_id=str(user_id),
    )

    return reminder


async def cancel_reminder(db: AsyncSession, task_id: int) -> None:
    """Cancel a pending reminder for a task."""
    stmt = select(Reminder).where(
        Reminder.task_id == task_id, Reminder.status == ReminderStatus.PENDING
    )
    reminder = (await db.execute(stmt)).scalar_one_or_none()
    if reminder:
        reminder.status = ReminderStatus.CANCELLED
        reminder.updated_at = datetime.now(timezone.utc)


async def get_reminder(db: AsyncSession, task_id: int) -> Reminder | None:
    """Get the active reminder for a task."""
    stmt = select(Reminder).where(
        Reminder.task_id == task_id, Reminder.status == ReminderStatus.PENDING
    )
    return (await db.execute(stmt)).scalar_one_or_none()
