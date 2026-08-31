import pytest
from pydantic import ValidationError

from app.config import Settings


def test_production_requires_service_api_key() -> None:
    with pytest.raises(ValidationError, match="SERVICE_API_KEY"):
        Settings(environment="production")


def test_production_rejects_placeholder_service_api_key() -> None:
    with pytest.raises(ValidationError, match="non-placeholder"):
        Settings(
            environment="production",
            service_api_key="replace-with-a-long-random-value",
        )
