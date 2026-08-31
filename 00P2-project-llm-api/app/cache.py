import json
from typing import Protocol

from redis.asyncio import Redis


class Cache(Protocol):
    async def get(self, key: str) -> dict | None: ...

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None: ...

    async def delete(self, key: str) -> None: ...


class RedisCache:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, key: str) -> dict | None:
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: dict, ttl_seconds: int) -> None:
        await self.redis.set(key, json.dumps(value), ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
