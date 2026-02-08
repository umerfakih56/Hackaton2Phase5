"""Handler for Dapr Jobs callback — triggers notification delivery."""

from typing import Any

import structlog

from app.services.notifier import send_notification

logger = structlog.get_logger()


async def handle_job_trigger(job_name: str, job_data: dict[str, Any]) -> None:
    """Handle a Dapr Jobs callback for a reminder.

    Called when the scheduled time arrives via:
    PUT /api/jobs/trigger/reminder-task-{task_id}
    """
    task_id = job_data.get("task_id")
    title = job_data.get("title", "Task reminder")
    user_id = job_data.get("user_id", "unknown")

    logger.info(
        "reminder_triggered",
        job_name=job_name,
        task_id=task_id,
        user_id=user_id,
    )

    await send_notification(
        user_id=user_id,
        task_id=task_id,
        title=f"Reminder: {title}",
        message=f"Your task '{title}' is due soon!",
    )
