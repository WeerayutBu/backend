from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.dependencies import Session
from app.models import User
from app.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/v1/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, session: Session) -> User:
    existing = await session.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=body.email, password_hash=hash_password(body.password))
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


@router.post("/token", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, session: Session) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, request.app.state.settings)
    return TokenResponse(access_token=token)

