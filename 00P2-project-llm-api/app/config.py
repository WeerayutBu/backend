"""Environment-backed configuration loaded at the outer application boundary."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_API_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    service_api_key: SecretStr | None = None
    provider_base_url: str = "https://api.openai.com/v1"
    provider_api_key: SecretStr = SecretStr("")
    default_model: str = "gpt-4.1-mini"
    redis_url: str = "redis://localhost:6379/0"
    request_timeout_seconds: float = 30
    max_retries: int = 2
    cache_ttl_seconds: int = 300

    @model_validator(mode="after")
    def validate_production_auth(self) -> "Settings":
        if self.environment != "production":
            return self
        if self.service_api_key is None:
            raise ValueError("LLM_API_SERVICE_API_KEY is required in production")
        key = self.service_api_key.get_secret_value()
        if len(key) < 32 or "replace" in key.lower() or "change-me" in key.lower():
            raise ValueError("LLM_API_SERVICE_API_KEY must be a non-placeholder secret")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
