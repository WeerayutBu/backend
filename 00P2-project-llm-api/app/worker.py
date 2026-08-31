"""Background entry point invoking the same ChatService application use case."""

from arq.connections import RedisSettings
from redis.asyncio import Redis

from app.cache import RedisCache
from app.config import get_settings
from app.provider import OpenAICompatibleProvider
from app.schemas import ChatRequest
from app.service import ChatService


async def startup(ctx: dict) -> None:
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    provider = OpenAICompatibleProvider(settings)
    ctx["redis"] = redis
    ctx["provider"] = provider
    ctx["service"] = ChatService(provider, RedisCache(redis), settings.cache_ttl_seconds)


async def shutdown(ctx: dict) -> None:
    await ctx["provider"].close()
    await ctx["redis"].aclose()


async def generate(ctx: dict, payload: dict) -> dict:
    command = ChatRequest.model_validate(payload).to_command()
    response = await ctx["service"].chat(command)
    return {
        "content": response.content,
        "model": response.model,
        "cached": response.cached,
    }


class WorkerSettings:
    functions = [generate]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    max_tries = 3
    job_timeout = 120
