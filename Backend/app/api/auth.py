"""
Auth API routes — register, login, refresh, me.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_current_user
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

AuthSvc = Annotated[AuthService, Depends(get_auth_service)]


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(body: RegisterRequest, svc: AuthSvc) -> TokenResponse:
    return await svc.register(body)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
)
async def login(body: LoginRequest, svc: AuthSvc) -> TokenResponse:
    return await svc.login(body)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a refresh token",
)
async def refresh(body: RefreshRequest, svc: AuthSvc) -> TokenResponse:
    return await svc.refresh(body.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
async def me(current_user: Annotated[dict, Depends(get_current_user)]) -> UserResponse:
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        created_at=current_user["created_at"],
    )
