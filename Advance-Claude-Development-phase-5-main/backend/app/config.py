"""Application configuration loaded from environment variables.

Supports optional Dapr Secrets API integration (T088):
When USE_DAPR_SECRETS=true, secrets are fetched from the Dapr sidecar
at startup instead of reading from .env directly.
"""

import httpx
import structlog
from pydantic_settings import BaseSettings

logger = structlog.get_logger()


class Settings(BaseSettings):
    """Backend API settings."""

    database_url: str = "postgresql+asyncpg://localhost/todo"
    dapr_http_port: int = 3500
    openai_api_key: str = ""
    backend_api_url: str = "http://localhost:8000"
    use_dapr_secrets: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    @property
    def dapr_base_url(self) -> str:
        return f"http://localhost:{self.dapr_http_port}"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def _fetch_dapr_secret(base_url: str, store: str, key: str) -> str | None:
    """Fetch a secret from Dapr Secrets API (synchronous, for startup)."""
    url = f"{base_url}/v1.0/secrets/{store}/{key}"
    try:
        resp = httpx.get(url, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            return data.get(key)
    except httpx.HTTPError as exc:
        logger.warning("dapr_secret_fetch_failed", key=key, error=str(exc))
    return None


settings = Settings()

# Override secrets from Dapr if enabled
if settings.use_dapr_secrets:
    secret_store = "kubernetes-secrets"
    base = settings.dapr_base_url

    db_url = _fetch_dapr_secret(base, secret_store, "DATABASE_URL")
    if db_url:
        settings.database_url = db_url

    api_key = _fetch_dapr_secret(base, secret_store, "OPENAI_API_KEY")
    if api_key:
        settings.openai_api_key = api_key

    logger.info("dapr_secrets_loaded", store=secret_store)
