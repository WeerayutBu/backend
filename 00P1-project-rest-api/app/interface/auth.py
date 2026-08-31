"""HTTP adapter translating authentication requests into use-case calls."""

from fastapi import APIRouter, HTTPException, status

from app.application.errors import EmailAlreadyRegistered, InvalidCredentials
from app.domain.entities import User
from app.interface.dependencies import AuthServiceDep
from app.interface.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, service: AuthServiceDep) -> User:
    try:
        return await service.register(str(body.email), body.password)
    except EmailAlreadyRegistered as exc:
        raise HTTPException(status_code=409, detail="Email already registered") from exc


@router.post("/token", response_model=TokenResponse)
async def login(body: LoginRequest, service: AuthServiceDep) -> TokenResponse:
    try:
        token = await service.login(str(body.email), body.password)
    except InvalidCredentials as exc:
        raise HTTPException(status_code=401, detail="Invalid email or password") from exc
    return TokenResponse(access_token=token)
