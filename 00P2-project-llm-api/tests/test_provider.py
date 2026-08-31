import httpx
import pytest

from app.config import Settings
from app.domain.models import ChatCommand, Message
from app.infrastructure.provider import OpenAICompatibleProvider


@pytest.mark.asyncio
async def test_provider_uses_versioned_chat_completions_path_without_empty_auth() -> None:
    seen_request: httpx.Request | None = None

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_request
        seen_request = request
        return httpx.Response(
            200,
            json={
                "model": "local-model",
                "choices": [{"message": {"content": "hello"}}],
            },
        )

    client = httpx.AsyncClient(
        base_url="http://ollama.test/v1/",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAICompatibleProvider(
        Settings(provider_base_url="http://ollama.test/v1", provider_api_key=""),
        client=client,
    )

    response = await provider.chat(ChatCommand(messages=(Message(role="user", content="hi"),)))
    await provider.close()

    assert response.content == "hello"
    assert seen_request is not None
    assert seen_request.url.path == "/v1/chat/completions"
    assert "Authorization" not in seen_request.headers


@pytest.mark.asyncio
async def test_provider_retries_temporary_failures() -> None:
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectError("temporary failure", request=request)
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"content": "recovered"}}],
            },
        )

    client = httpx.AsyncClient(
        base_url="http://provider.test/v1/",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAICompatibleProvider(
        Settings(max_retries=1),
        client=client,
    )

    response = await provider.chat(ChatCommand(messages=(Message(role="user", content="hi"),)))
    await provider.close()

    assert response.content == "recovered"
    assert calls == 2
