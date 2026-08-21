import logging

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

logger = logging.getLogger("auth-service")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    logger.info(f"Registration attempt: email={data.email}")
    user = await auth_service.register(data)
    logger.info(f"Registration successful: email={data.email}, user_id={user.id}")
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    logger.info(f"Login attempt: email={data.email}")
    try:
        token = await auth_service.login(data)
    except Exception as e:
        logger.warning(f"Login failed: email={data.email}, reason={str(e)}")
        raise
    logger.info(f"Login successful: email={data.email}")
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
