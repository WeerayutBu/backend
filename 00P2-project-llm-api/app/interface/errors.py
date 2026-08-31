"""Translate application failures into stable HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.errors import JobNotFound, ProviderUnavailable, QueueUnavailable


def error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def provider_unavailable(_request: Request, _error: ProviderUnavailable) -> JSONResponse:
    return error_response(status.HTTP_502_BAD_GATEWAY, "Model provider request failed")


async def queue_unavailable(_request: Request, _error: QueueUnavailable) -> JSONResponse:
    return error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "Job queue unavailable")


async def job_not_found(_request: Request, _error: JobNotFound) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "Job not found")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ProviderUnavailable, provider_unavailable)
    app.add_exception_handler(QueueUnavailable, queue_unavailable)
    app.add_exception_handler(JobNotFound, job_not_found)
