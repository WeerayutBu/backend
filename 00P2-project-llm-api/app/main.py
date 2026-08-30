import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from arq.connections import RedisSettings, create_pool
from fastapi import FastAPI, Request, Response
from redis.asyncio import Redis

from app.api import router
from app.cache import RedisCache
from app.config import Settings, get_settings
from app.logging import configure_logging
from app.provider import OpenAICompatibleProvider
from app.queue import ArqJobQueue, JobQueue
from app.service import ChatService

logger = logging.getLogger("app.http")


def create_app(
    settings: Settings | None = None,
    chat_service: ChatService | None = None,
    job_queue: JobQueue | None = None,
) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        if chat_service is not None and job_queue is not None:
            app.state.chat_service = chat_service
            app.state.job_queue = job_queue
            yield
            return

        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        queue_redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
        provider = OpenAICompatibleProvider(settings)

        app.state.chat_service = ChatService(
            provider=provider,
            cache=RedisCache(redis),
            cache_ttl_seconds=settings.cache_ttl_seconds,
        )
        app.state.job_queue = ArqJobQueue(queue_redis)
        yield
        await provider.close()
        await redis.aclose()
        await queue_redis.aclose()

    app = FastAPI(title="LLM API", version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def log_request(request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    app.include_router(router)
    return app


app = create_app()
