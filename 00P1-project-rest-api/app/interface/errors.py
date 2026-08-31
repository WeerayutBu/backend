"""Translate application errors into stable HTTP responses."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.application.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
    InvalidInput,
    TaskNotFound,
)


def error_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def email_exists(_request: Request, _error: EmailAlreadyRegistered) -> JSONResponse:
    return error_response(status.HTTP_409_CONFLICT, "Email already registered")


async def invalid_credentials(_request: Request, _error: InvalidCredentials) -> JSONResponse:
    response = error_response(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    response.headers["WWW-Authenticate"] = "Bearer"
    return response


async def invalid_input(_request: Request, error: InvalidInput) -> JSONResponse:
    return error_response(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))


async def task_not_found(_request: Request, _error: TaskNotFound) -> JSONResponse:
    return error_response(status.HTTP_404_NOT_FOUND, "Task not found")


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EmailAlreadyRegistered, email_exists)
    app.add_exception_handler(InvalidCredentials, invalid_credentials)
    app.add_exception_handler(InvalidInput, invalid_input)
    app.add_exception_handler(TaskNotFound, task_not_found)
