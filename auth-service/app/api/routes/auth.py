from fastapi import APIRouter, Depends

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.user import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    token = await auth_service.login(data)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
