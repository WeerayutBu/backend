import pytest

from app.application.errors import CacheUnavailable
from app.application.services import ChatService
from app.domain.models import ChatCommand, ChatResult, Message

pytestmark = pytest.mark.asyncio


class UnavailableCache:
    async def get(self, key: str) -> ChatResult | None:
        raise CacheUnavailable

    async def set(self, key: str, value: ChatResult, ttl_seconds: int) -> None:
        raise CacheUnavailable

    async def delete(self, key: str) -> None:
        raise CacheUnavailable


class FakeProvider:
    async def chat(self, command: ChatCommand) -> ChatResult:
        return ChatResult(content="available", model="test-model")


async def test_chat_continues_when_cache_is_unavailable() -> None:
    service = ChatService(FakeProvider(), UnavailableCache(), 60)
    command = ChatCommand(messages=(Message(role="user", content="hello"),))

    response = await service.chat(command)

    assert response.content == "available"
