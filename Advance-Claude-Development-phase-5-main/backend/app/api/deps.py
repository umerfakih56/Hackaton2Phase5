"""Dependency injection for FastAPI routes."""

import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session


async def get_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AsyncSession, None]:
    yield session


async def get_current_user_id(
    authorization: str = Header(..., description="Bearer JWT token"),
) -> uuid.UUID:
    """Extract user ID from JWT token.

    In Phase V this is a simplified implementation. Better Auth
    handles the full JWT validation in the frontend; backend
    trusts forwarded user context.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    # Simplified: extract user_id from token claims
    # In production, validate JWT signature with Better Auth public key
    try:
        # For Phase V, accept a UUID directly as a simplified token
        return uuid.UUID(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
