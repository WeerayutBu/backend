"""Environment-backed configuration loaded at the application boundary."""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="REST_API_",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/app"
    jwt_secret: SecretStr
    access_token_minutes: int = 30

    @model_validator(mode="after")
    def validate_secret(self) -> "Settings":
        secret = self.jwt_secret.get_secret_value()
        if len(secret) < 32:
            raise ValueError("REST_API_JWT_SECRET must contain at least 32 characters")
        if self.environment == "production" and (
            "replace" in secret.lower() or "change-me" in secret.lower()
        ):
            raise ValueError("REST_API_JWT_SECRET still contains a placeholder")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
