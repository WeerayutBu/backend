from typing import Any

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.models import ChatRequest, ChatResponse, JobStatus
from app.service import ChatService


class MemoryCache:
    def __init__(self) -> None:
        self.values: dict[str, dict] = {}

    async def get(self, key: str) -> dict | None:
        return self.values.get(key)

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        self.values[key] = value


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def chat(self, request: ChatRequest) -> ChatResponse:
        self.calls += 1
        return ChatResponse(content="Hello from the model", model=request.model or "test-model")


class FakeQueue:
    async def enqueue(self, request: ChatRequest) -> str:
        return "job-123"

    async def status(self, job_id: str) -> JobStatus:
        return JobStatus(job_id=job_id, status="complete")


def make_client() -> tuple[TestClient, FakeProvider]:
    provider = FakeProvider()
    service = ChatService(provider, MemoryCache(), cache_ttl_seconds=60)
    app = create_app(Settings(), chat_service=service, job_queue=FakeQueue())  # type: ignore[arg-type]
    return TestClient(app), provider


def payload(**overrides: Any) -> dict:
    body = {"messages": [{"role": "user", "content": "Hello"}]}
    body.update(overrides)
    return body


def test_health() -> None:
    client, _ = make_client()
    with client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_chat_returns_and_caches_response() -> None:
    client, provider = make_client()
    with client:
        first = client.post("/v1/chat", json=payload())
        second = client.post("/v1/chat", json=payload())

    assert first.status_code == 200
    assert first.json()["cached"] is False
    assert second.json()["cached"] is True
    assert provider.calls == 1


def test_chat_validates_input() -> None:
    client, _ = make_client()
    with client:
        response = client.post("/v1/chat", json=payload(temperature=3))
    assert response.status_code == 422


def test_create_and_read_job() -> None:
    client, _ = make_client()
    with client:
        created = client.post("/v1/jobs", json=payload())
        status = client.get("/v1/jobs/job-123")

    assert created.status_code == 202
    assert created.json() == {"job_id": "job-123", "status": "queued"}
    assert status.status_code == 200
    assert status.json()["status"] == "complete"
