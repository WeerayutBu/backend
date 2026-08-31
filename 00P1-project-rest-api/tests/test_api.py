from collections.abc import AsyncIterator

import httpx
import pytest

from app.config import Settings
from app.main import create_app

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(
        Settings(
            database_url="sqlite+aiosqlite://",
            jwt_secret="test-secret-with-at-least-32-characters",
        ),
        create_schema=True,
    )
    transport = httpx.ASGITransport(app=app)
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:
        yield test_client


async def register(client: httpx.AsyncClient, email: str = "ada@example.com") -> dict:
    response = await client.post(
        "/v1/auth/register",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 201
    return response.json()


async def token(client: httpx.AsyncClient, email: str = "ada@example.com") -> str:
    response = await client.post(
        "/v1/auth/token",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


async def test_health_adds_request_id(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


async def test_register_login_and_reject_duplicate(client: httpx.AsyncClient) -> None:
    user = await register(client)
    assert user["email"] == "ada@example.com"
    assert await token(client)

    duplicate = await client.post(
        "/v1/auth/register",
        json={"email": "ada@example.com", "password": "password123"},
    )
    assert duplicate.status_code == 409
    assert await register(client, "grace@example.com")


async def test_tasks_require_authentication(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/tasks")
    assert response.status_code == 401


async def test_task_crud(client: httpx.AsyncClient) -> None:
    await register(client)
    headers = auth_headers(await token(client))

    created = await client.post(
        "/v1/tasks",
        headers=headers,
        json={"title": "Learn transactions", "description": "Build a REST API"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    listed = await client.get("/v1/tasks", headers=headers)
    assert [task["id"] for task in listed.json()] == [task_id]

    updated = await client.patch(
        f"/v1/tasks/{task_id}",
        headers=headers,
        json={"completed": True},
    )
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    deleted = await client.delete(f"/v1/tasks/{task_id}", headers=headers)
    assert deleted.status_code == 204
    missing = await client.get(f"/v1/tasks/{task_id}", headers=headers)
    assert missing.status_code == 404


async def test_tasks_are_private_and_paginated(client: httpx.AsyncClient) -> None:
    await register(client, "ada@example.com")
    ada_headers = auth_headers(await token(client, "ada@example.com"))
    created = await client.post("/v1/tasks", headers=ada_headers, json={"title": "Private"})
    task_id = created.json()["id"]

    await register(client, "grace@example.com")
    grace_headers = auth_headers(await token(client, "grace@example.com"))

    hidden = await client.get(f"/v1/tasks/{task_id}", headers=grace_headers)
    limited = await client.get("/v1/tasks?limit=1&offset=0", headers=ada_headers)

    assert hidden.status_code == 404
    assert [task["id"] for task in limited.json()] == [task_id]
