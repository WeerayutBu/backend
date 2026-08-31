"""Interfaces required by the application services."""

from typing import Protocol

from app.domain.models import ChatCommand, ChatResult, JobResult


class Cache(Protocol):
    async def get(self, key: str) -> ChatResult | None: ...

    async def set(self, key: str, value: ChatResult, ttl_seconds: int) -> None: ...

    async def delete(self, key: str) -> None: ...


class LLMProvider(Protocol):
    async def chat(self, command: ChatCommand) -> ChatResult: ...


class JobQueue(Protocol):
    async def enqueue(self, command: ChatCommand) -> str: ...

    async def status(self, job_id: str) -> JobResult: ...
