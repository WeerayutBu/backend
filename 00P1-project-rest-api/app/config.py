from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="REST_API_",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    jwt_secret: str = Field(default="development-only-secret-change-me-1234", repr=False)
    access_token_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
