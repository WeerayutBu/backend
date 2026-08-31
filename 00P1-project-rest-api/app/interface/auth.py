"""HTTP adapter translating authentication requests into use-case calls."""

from fastapi import APIRouter, status

from app.domain.entities import User
from app.interface.dependencies import AuthServiceDep
from app.interface.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, service: AuthServiceDep) -> User:
    return await service.register(str(body.email), body.password)


@router.post("/token", response_model=TokenResponse)
async def login(body: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    token = await service.login(str(body.email), body.password)
    return TokenResponse(access_token=token)
