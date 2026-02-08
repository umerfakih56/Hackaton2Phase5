"""Handler for task-completed events — creates the next recurring occurrence."""

from typing import Any

import httpx
import structlog

from app.config import settings
from app.services.recurrence import compute_next_occurrence

logger = structlog.get_logger()


async def _check_idempotency(correlation_id: str) -> bool:
    """Check if this event was already processed using Dapr State Store."""
    url = f"{settings.dapr_base_url}/v1.0/state/statestore/{correlation_id}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=3.0)
            if resp.status_code == 200 and resp.text:
                return True  # Already processed
    except httpx.HTTPError:
        pass
    return False


async def _mark_processed(correlation_id: str) -> None:
    """Mark this event as processed in Dapr State Store."""
    url = f"{settings.dapr_base_url}/v1.0/state/statestore"
    payload = [{"key": correlation_id, "value": "processed"}]
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, timeout=3.0)
    except httpx.HTTPError as exc:
        logger.warning("state_store_write_failed", error=str(exc))


async def handle_task_completed(event_data: dict[str, Any]) -> None:
    """Process a task-completed event and create the next recurring occurrence.

    Steps:
    1. Check idempotency via Dapr State Store (correlation_id).
    2. Verify the task is recurring.
    3. Compute next occurrence date.
    4. Create new task via Backend API.
    5. Mark event as processed.
    """
    correlation_id = event_data.get("id", "")
    data = event_data.get("data", {})

    # 1. Idempotency check
    if await _check_idempotency(correlation_id):
        logger.info("duplicate_event_skipped", correlation_id=correlation_id)
        return

    task_data = data.get("task_data", {})
    event_type = data.get("event_type", "")

    # Only handle completed events for recurring tasks
    if event_type != "completed":
        return

    if not task_data.get("is_recurring"):
        logger.debug("non_recurring_task_skipped", task_id=task_data.get("id"))
        return

    recurrence_pattern = task_data.get("recurrence_pattern")
    if not recurrence_pattern:
        logger.warning("missing_recurrence_pattern", task_id=task_data.get("id"))
        return

    # 2. Compute next occurrence
    from datetime import datetime, timezone

    completed_at = datetime.now(timezone.utc)
    timestamp = data.get("timestamp")
    if timestamp:
        try:
            completed_at = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            pass

    next_due = compute_next_occurrence(completed_at, recurrence_pattern)

    # 3. Create next occurrence via Backend API (Dapr Service Invocation)
    new_task_payload = {
        "title": task_data.get("title", "Recurring task"),
        "description": task_data.get("description"),
        "priority": task_data.get("priority", "medium"),
        "tags": task_data.get("tags", []),
        "due_date": next_due.isoformat(),
        "is_recurring": True,
        "recurrence_pattern": {
            **recurrence_pattern,
            "parent_task_id": task_data.get("id"),
        },
        "reminder_offset": task_data.get("reminder_offset"),
    }

    user_id = data.get("user_id", "")
    create_url = (
        f"{settings.dapr_base_url}/v1.0/invoke/backend/method/api/tasks"
    )

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                create_url,
                json=new_task_payload,
                headers={
                    "Authorization": f"Bearer {user_id}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            new_task = resp.json()
            logger.info(
                "next_occurrence_created",
                original_task_id=task_data.get("id"),
                new_task_id=new_task.get("id"),
                next_due=next_due.isoformat(),
            )
    except httpx.HTTPError as exc:
        logger.error(
            "create_next_occurrence_failed",
            task_id=task_data.get("id"),
            error=str(exc),
        )
        return  # Don't mark as processed so it retries

    # 4. Mark processed
    await _mark_processed(correlation_id)
