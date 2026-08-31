import pytest
from pydantic import ValidationError

from app.config import Settings


def test_production_rejects_placeholder_secret() -> None:
    with pytest.raises(ValidationError, match="placeholder"):
        Settings(
            environment="production",
            jwt_secret="replace-with-a-long-random-value",
        )
