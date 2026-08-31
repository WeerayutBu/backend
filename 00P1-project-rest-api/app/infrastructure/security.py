"""Password-hashing and JWT adapters implementing application ports."""

from datetime import UTC, datetime, timedelta

import jwt
from anyio import to_thread
from pwdlib import PasswordHash

from app.application.errors import InvalidToken
from app.config import Settings


class ArgonPasswordHasher:
    def __init__(self) -> None:
        self.password_hash = PasswordHash.recommended()

    async def hash(self, password: str) -> str:
        return await to_thread.run_sync(self.password_hash.hash, password)

    async def verify(self, password: str, password_hash: str) -> bool:
        return await to_thread.run_sync(self.password_hash.verify, password, password_hash)


class JWTTokenService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create(self, user_id: int) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.access_token_minutes
        )
        return jwt.encode(
            {"sub": str(user_id), "exp": expires_at},
            self.settings.jwt_secret.get_secret_value(),
            "HS256",
        )

    def read_user_id(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret.get_secret_value(),
                algorithms=["HS256"],
            )
            return int(payload["sub"])
        except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
            raise InvalidToken from exc
