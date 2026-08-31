"""Redis adapter implementing the cache port."""

import json
from dataclasses import asdict

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.application.errors import CacheUnavailable
from app.domain.models import ChatResult


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> ChatResult | None:
        try:
            value = await self.redis.get(key)
            return ChatResult(**json.loads(value)) if value else None
        except (RedisError, json.JSONDecodeError, TypeError, ValueError) as exc:
            raise CacheUnavailable from exc

    async def set(self, key: str, value: ChatResult, ttl_seconds: int) -> None:
        try:
            await self.redis.set(key, json.dumps(asdict(value)), ex=ttl_seconds)
        except RedisError as exc:
            raise CacheUnavailable from exc

    async def delete(self, key: str) -> None:
        try:
            await self.redis.delete(key)
        except RedisError as exc:
            raise CacheUnavailable from exc
