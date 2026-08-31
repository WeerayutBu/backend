"""Application use cases independent of HTTP, Redis, ARQ, and provider clients."""

import hashlib
import json
import logging
from dataclasses import asdict, replace

from app.application.errors import CacheUnavailable
from app.application.ports import Cache, JobQueue, LLMProvider
from app.domain.models import ChatCommand, ChatResult, JobResult

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        provider: LLMProvider,
        cache: Cache,
        cache_ttl_seconds: int,
        cache_namespace: str = "default",
    ) -> None:
        self.provider = provider
        self.cache = cache
        self.cache_ttl_seconds = cache_ttl_seconds
        self.cache_namespace = cache_namespace

    async def chat(self, command: ChatCommand) -> ChatResult:
        key = self._cache_key(command)
        try:
            cached = await self.cache.get(key)
        except CacheUnavailable:
            logger.warning("cache_read_failed", exc_info=True)
            cached = None
        if cached:
            return replace(cached, cached=True)

        response = await self.provider.chat(command)
        try:
            await self.cache.set(key, response, self.cache_ttl_seconds)
        except CacheUnavailable:
            logger.warning("cache_write_failed", exc_info=True)
        return response

    def _cache_key(self, command: ChatCommand) -> str:
        payload = {"namespace": self.cache_namespace, "command": asdict(command)}
        body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return f"chat:{hashlib.sha256(body.encode()).hexdigest()}"


class JobService:
    def __init__(self, queue: JobQueue) -> None:
        self.queue = queue

    async def create_job(self, command: ChatCommand) -> str:
        return await self.queue.enqueue(command)

    async def get_job(self, job_id: str) -> JobResult:
        return await self.queue.status(job_id)
