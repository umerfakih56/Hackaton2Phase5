"""Notification Service configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dapr_http_port: int = 3500

    @property
    def dapr_base_url(self) -> str:
        return f"http://localhost:{self.dapr_http_port}"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
