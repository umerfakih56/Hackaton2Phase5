"""Recurring Task Service — FastAPI app with Dapr subscription."""

from fastapi import FastAPI, Request

from app.handlers.task_completed import handle_task_completed
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Recurring Task Service",
    version="0.1.0",
    description="Consumes task-completed events and creates next recurring occurrences.",
)


@app.get("/healthz")
async def liveness():
    return {"status": "ok"}


@app.get("/readyz")
async def readiness():
    return {"status": "ready"}


@app.get("/dapr/subscribe")
async def dapr_subscribe():
    """Declare Dapr Pub/Sub subscriptions."""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-completed",
        }
    ]


@app.post("/events/task-completed")
async def on_task_event(request: Request):
    """Handle incoming task events from Kafka via Dapr."""
    event = await request.json()
    await handle_task_completed(event)
    return {"status": "SUCCESS"}
