"""Application use cases independent of HTTP, Redis, ARQ, and provider clients."""

import hashlib
import json
from dataclasses import asdict, replace

from app.application.ports import Cache, JobQueue, LLMProvider
from app.domain.models import ChatCommand, ChatResult, JobResult


class ChatService:
    def __init__(self, provider: LLMProvider, cache: Cache, cache_ttl_seconds: int) -> None:
        self.provider = provider
        self.cache = cache
        self.cache_ttl_seconds = cache_ttl_seconds

    async def chat(self, command: ChatCommand) -> ChatResult:
        key = self._cache_key(command)
        cached = await self.cache.get(key)
        if cached:
            return replace(cached, cached=True)

        response = await self.provider.chat(command)
        await self.cache.set(key, response, self.cache_ttl_seconds)
        return response

    @staticmethod
    def _cache_key(command: ChatCommand) -> str:
        body = json.dumps(asdict(command), sort_keys=True, separators=(",", ":"))
        return f"chat:{hashlib.sha256(body.encode()).hexdigest()}"


class JobService:
    def __init__(self, queue: JobQueue) -> None:
        self.queue = queue

    async def create_job(self, command: ChatCommand) -> str:
        return await self.queue.enqueue(command)

    async def get_job(self, job_id: str) -> JobResult:
        return await self.queue.status(job_id)
