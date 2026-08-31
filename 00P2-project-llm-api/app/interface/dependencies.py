"""FastAPI dependencies exposing application services to HTTP routes."""

import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from app.application.services import ChatService, JobService

service_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
JobServiceDep = Annotated[JobService, Depends(get_job_service)]


async def require_service_api_key(
    request: Request,
    provided: Annotated[str | None, Depends(service_api_key)],
) -> None:
    configured = request.app.state.settings.service_api_key
    if configured is None:
        return
    expected = configured.get_secret_value()
    if provided is None or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
