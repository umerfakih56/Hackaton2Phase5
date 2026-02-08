"""Health check endpoints for liveness and readiness probes."""

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import settings

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    summary="Liveness probe",
    description=(
        "Returns 200 if the service process is running. "
        "Used by Kubernetes liveness probes."
    ),
)
async def liveness():
    return {"status": "ok"}


@router.get(
    "/readyz",
    summary="Readiness probe",
    description=(
        "Checks database connectivity and Dapr sidecar health. "
        "Returns 503 if any dependency is unavailable."
    ),
)
async def readiness(db: AsyncSession = Depends(get_db)):
    checks: dict[str, str] = {}

    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"

    # Check Dapr sidecar
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.dapr_base_url}/v1.0/healthz", timeout=2.0
            )
            checks["dapr"] = "ok" if resp.status_code == 204 else "unavailable"
    except Exception:
        checks["dapr"] = "unavailable"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    status = "ready" if all_ok else "not_ready"

    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=status_code, content={"status": status, "checks": checks}
    )
