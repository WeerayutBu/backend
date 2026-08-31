"""Redis adapter implementing the cache port."""

import json
from dataclasses import asdict

from redis.asyncio import Redis

from app.domain.models import ChatResult


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> ChatResult | None:
        value = await self.redis.get(key)
        return ChatResult(**json.loads(value)) if value else None

    async def set(self, key: str, value: ChatResult, ttl_seconds: int) -> None:
        await self.redis.set(key, json.dumps(asdict(value)), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
