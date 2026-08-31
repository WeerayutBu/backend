"""Composition root: configure FastAPI and connect infrastructure adapters."""

import logging
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.application.services import AuthService, TaskService
from app.config import Settings, get_settings
from app.infrastructure.database import Base
from app.infrastructure.repositories import SqlAlchemyTaskRepository, SqlAlchemyUserRepository
from app.infrastructure.security import ArgonPasswordHasher, JWTTokenService
from app.interface.auth import router as auth_router
from app.interface.tasks import router as tasks_router
from app.logging import configure_logging

logger = logging.getLogger("app.http")


def create_app(settings: Settings | None = None, *, create_schema: bool = False) -> FastAPI:
    settings = settings or get_settings()
    engine_options = {}
    if settings.database_url.startswith("sqlite"):
        engine_options["poolclass"] = StaticPool
    engine = create_async_engine(settings.database_url, **engine_options)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    passwords = ArgonPasswordHasher()
    tokens = JWTTokenService(settings)

    # Only the composition root knows which concrete adapters each use case receives.
    def auth_service_factory(session: AsyncSession) -> AuthService:
        return AuthService(SqlAlchemyUserRepository(session), passwords, tokens)

    def task_service_factory(session: AsyncSession) -> TaskService:
        return TaskService(SqlAlchemyTaskRepository(session))

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        app.state.session_factory = session_factory
        app.state.auth_service_factory = auth_service_factory
        app.state.task_service_factory = task_service_factory
        if create_schema:
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
        yield
        await engine.dispose()

    app = FastAPI(title="REST API", version="0.1.0", lifespan=lifespan)

    @app.middleware("http")
    async def log_request(request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            },
        )
        return response

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router)
    app.include_router(tasks_router)
    return app


app = create_app()
