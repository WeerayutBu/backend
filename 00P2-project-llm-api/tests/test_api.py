from collections.abc import AsyncIterator
from typing import Any

import httpx
import pytest

from app.application.services import ChatService, JobService
from app.config import Settings
from app.domain.models import ChatCommand, ChatResult, JobResult
from app.main import create_app


class MemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, ChatResult] = {}

    async def get(self, key: str) -> ChatResult | None:
        return self.values.get(key)

    async def set(self, key: str, value: ChatResult, ttl_seconds: int) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def chat(self, command: ChatCommand) -> ChatResult:
        self.calls += 1
        return ChatResult(content="Hello from the model", model=command.model or "test-model")


class FakeQueue:
    async def enqueue(self, command: ChatCommand) -> str:
        return "job-123"

    async def status(self, job_id: str) -> JobResult:
        return JobResult(job_id=job_id, status="complete")


def make_app() -> tuple[Any, FakeProvider]:
    provider = FakeProvider()
    service = ChatService(provider, MemoryCache(), cache_ttl_seconds=60)
    app = create_app(Settings(), chat_service=service, job_service=JobService(FakeQueue()))
    return app, provider


@pytest.fixture
async def client() -> AsyncIterator[tuple[httpx.AsyncClient, FakeProvider]]:
    app, provider = make_app()
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client, provider


def payload(**overrides: Any) -> dict:
    body = {"messages": [{"role": "user", "content": "Hello"}]}
    body.update(overrides)
    return body


async def test_health(client: tuple[httpx.AsyncClient, FakeProvider]) -> None:
    test_client, _ = client
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


async def test_chat_returns_and_caches_response(
    client: tuple[httpx.AsyncClient, FakeProvider],
) -> None:
    test_client, provider = client
    first = await test_client.post("/v1/chat", json=payload())
    second = await test_client.post("/v1/chat", json=payload())

    assert first.status_code == 200
    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert provider.calls == 1


async def test_chat_validates_input(
    client: tuple[httpx.AsyncClient, FakeProvider],
) -> None:
    test_client, _ = client
    response = await test_client.post("/v1/chat", json=payload(temperature=3))
    assert response.status_code == 422


async def test_create_and_read_job(
    client: tuple[httpx.AsyncClient, FakeProvider],
) -> None:
    test_client, _ = client
    created = await test_client.post("/v1/jobs", json=payload())
    status = await test_client.get("/v1/jobs/job-123")

    assert created.status_code == 202
    assert created.json() == {"job_id": "job-123", "status": "queued"}
    assert status.status_code == 200
    assert status.json()["status"] == "complete"
