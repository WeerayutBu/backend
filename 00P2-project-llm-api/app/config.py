"""Environment-backed configuration loaded at the outer application boundary."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_API_",
        extra="ignore",
    )

    provider_base_url: str = "https://api.openai.com/v1"
    provider_api_key: str = Field(default="", repr=False)
    default_model: str = "gpt-4.1-mini"
    redis_url: str = "redis://localhost:6379/0"
    request_timeout_seconds: float = 30
    max_retries: int = 2
    cache_ttl_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
