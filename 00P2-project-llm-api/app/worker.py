"""Worker composition root connecting ARQ, Redis, provider, and ChatService."""

from arq.connections import RedisSettings
from redis.asyncio import Redis

from app.application.services import ChatService
from app.config import get_settings
from app.infrastructure.cache import RedisCache
from app.infrastructure.provider import OpenAICompatibleProvider
from app.interface.worker import generate


async def startup(ctx: dict) -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    provider = OpenAICompatibleProvider(settings)
    ctx["redis"] = redis
    ctx["provider"] = provider
    cache_namespace = f"{settings.provider_base_url}|{settings.default_model}"
    ctx["service"] = ChatService(
        provider,
        RedisCache(redis),
        settings.cache_ttl_seconds,
        cache_namespace,
    )


async def shutdown(ctx: dict) -> None:
    try:
        await ctx["provider"].close()
    finally:
        await ctx["redis"].aclose()


class WorkerSettings:
    functions = [generate]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_tries = 3
    job_timeout = 120
