"""FastAPI application entry point with Dapr subscription endpoint."""

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.tags import router as tags_router
from app.api.tasks import router as tasks_router
from app.config import settings
from app.logging_config import generate_correlation_id, setup_logging

# Initialize structured logging
setup_logging()
logger = structlog.get_logger()

app = FastAPI(
    title="Todo Chatbot API",
    version="0.1.0",
    description=(
        "Event-driven todo chatbot backend with Dapr "
        "integration.\n\nAll infrastructure access goes "
        "through Dapr sidecars. The backend publishes "
        "events to Kafka via Dapr Pub/Sub and serves as "
        "the primary API for the frontend and AI chat agent."
    ),
    openapi_tags=[
        {
            "name": "tasks",
            "description": "Task CRUD with priority, tags, filtering",
        },
        {
            "name": "tags",
            "description": "Tag management and autocomplete",
        },
        {
            "name": "chat",
            "description": "AI chat for task management",
        },
        {
            "name": "health",
            "description": "Liveness and readiness probes",
        },
    ],
)

_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]
if settings.cors_origins:
    _allowed_origins = settings.cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    """Inject a correlation ID into every request for distributed tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", generate_correlation_id())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

    logger.info("request_started", method=request.method, path=request.url.path)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    logger.info("request_completed", status_code=response.status_code)

    return response


# Health endpoints (no prefix)
app.include_router(health_router)

# API routers
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(chat_router)


@app.get("/dapr/subscribe", tags=["health"])
async def dapr_subscribe():
    """Dapr programmatic subscription declaration.

    Dapr calls this endpoint on startup to discover topic subscriptions.
    The backend API does not consume events — it only publishes.
    Consumer services (recurring-task, notification) declare their own
    subscriptions.
    """
    return []
