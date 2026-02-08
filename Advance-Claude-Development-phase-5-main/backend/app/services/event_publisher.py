"""Dapr Pub/Sub event publisher using httpx — no direct Kafka client."""

import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger()

PUBSUB_NAME = "kafka-pubsub"


async def publish_event(
    topic: str,
    event_type: str,
    data: dict[str, Any],
    source: str = "/api/tasks",
) -> None:
    """Publish a CloudEvents-formatted event via Dapr Pub/Sub HTTP API."""
    correlation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    cloud_event = {
        "specversion": "1.0",
        "type": f"com.todo.{event_type}",
        "source": source,
        "id": correlation_id,
        "time": now,
        "datacontenttype": "application/json",
        "data": {**data, "timestamp": now},
    }

    url = f"{settings.dapr_base_url}/v1.0/publish/{PUBSUB_NAME}/{topic}"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                json=cloud_event,
                headers={"Content-Type": "application/cloudevents+json"},
                timeout=5.0,
            )
            resp.raise_for_status()
            logger.info(
                "event_published",
                topic=topic,
                event_type=event_type,
                correlation_id=correlation_id,
            )
    except httpx.HTTPError as exc:
        logger.warning(
            "event_publish_failed",
            topic=topic,
            event_type=event_type,
            correlation_id=correlation_id,
            error=str(exc),
        )
        # Per error handling contract: do NOT block the user operation.
        # The event will be retried via outbox pattern or Dapr retry policy.


async def publish_task_event(
    event_type: str,
    task_id: int,
    task_data: dict[str, Any],
    user_id: str,
) -> None:
    """Convenience wrapper for task-events topic."""
    await publish_event(
        topic="task-events",
        event_type=f"task.{event_type}",
        data={
            "event_type": event_type,
            "task_id": task_id,
            "task_data": task_data,
            "user_id": user_id,
        },
    )


async def publish_reminder_event(
    task_id: int,
    title: str,
    due_at: str,
    remind_at: str,
    user_id: str,
) -> None:
    """Publish a reminder event to the reminders topic."""
    await publish_event(
        topic="reminders",
        event_type="reminder.scheduled",
        data={
            "task_id": task_id,
            "title": title,
            "due_at": due_at,
            "remind_at": remind_at,
            "user_id": user_id,
        },
    )
