"""FastAPI dependencies connecting HTTP requests to application services."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.domain import User
from app.errors import InvalidToken
from app.services import AuthService, TaskService

bearer = HTTPBearer(auto_error=False)
Session = Annotated[AsyncSession, Depends(get_session)]


def get_auth_service(request: Request, session: Session) -> AuthService:
    return request.app.state.auth_service_factory(session)


def get_task_service(request: Request, session: Session) -> TaskService:
    return request.app.state.task_service_factory(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


async def get_current_user(
    service: AuthServiceDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized

    try:
        return await service.authenticate(credentials.credentials)
    except InvalidToken as exc:
        raise unauthorized from exc


CurrentUser = Annotated[User, Depends(get_current_user)]
