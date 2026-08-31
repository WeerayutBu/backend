"""FastAPI dependencies exposing application services to HTTP routes."""

from typing import Annotated

from fastapi import Depends, Request

from app.application.services import ChatService, JobService


def get_chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
JobServiceDep = Annotated[JobService, Depends(get_job_service)]
