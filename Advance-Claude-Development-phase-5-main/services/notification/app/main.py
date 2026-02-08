"""Notification Service — FastAPI app with Dapr subscription and Jobs callback."""

from fastapi import FastAPI, Request

from app.handlers.job_trigger import handle_job_trigger
from app.handlers.reminder_scheduled import handle_reminder_scheduled
from app.logging_config import setup_logging

setup_logging()

app = FastAPI(
    title="Notification Service",
    version="0.1.0",
    description="Consumes reminder events and delivers notifications via Dapr Jobs.",
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
            "topic": "reminders",
            "route": "/events/reminder-scheduled",
        }
    ]


@app.post("/events/reminder-scheduled")
async def on_reminder_event(request: Request):
    """Handle incoming reminder events from Kafka via Dapr."""
    event = await request.json()
    await handle_reminder_scheduled(event)
    return {"status": "SUCCESS"}


@app.put("/api/jobs/trigger/{job_name}")
async def on_job_trigger(job_name: str, request: Request):
    """Dapr Jobs callback — fired when a scheduled reminder time arrives."""
    body = await request.json()
    await handle_job_trigger(job_name, body)
    return {"status": "SUCCESS"}
