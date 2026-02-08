"""Handler for reminder-scheduled events — schedules Dapr Jobs."""

from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()


async def handle_reminder_scheduled(event_data: dict[str, Any]) -> None:
    """Process a reminder event and schedule a Dapr Job.

    The Dapr Jobs API will call back at the scheduled time via
    PUT /api/jobs/trigger/reminder-task-{task_id}.
    """
    data = event_data.get("data", {})

    task_id = data.get("task_id")
    remind_at = data.get("remind_at")
    user_id = data.get("user_id", "")
    title = data.get("title", "")

    if not task_id or not remind_at:
        logger.warning("invalid_reminder_event", data=data)
        return

    job_name = f"reminder-task-{task_id}"

    # Schedule via Dapr Jobs API (v1.0-alpha1)
    job_url = f"{settings.dapr_base_url}/v1.0-alpha1/jobs/{job_name}"
    job_payload = {
        "schedule": f"@at {remind_at}",
        "data": {
            "task_id": task_id,
            "title": title,
            "user_id": user_id,
        },
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                job_url, json=job_payload, timeout=5.0
            )
            resp.raise_for_status()
            logger.info(
                "dapr_job_scheduled",
                job_name=job_name,
                remind_at=remind_at,
                task_id=task_id,
            )
    except httpx.HTTPError as exc:
        logger.error(
            "dapr_job_schedule_failed",
            job_name=job_name,
            error=str(exc),
        )
