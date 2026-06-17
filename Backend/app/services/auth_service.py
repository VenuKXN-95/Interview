"""
Auth service — register, login, refresh, and current-user resolution.
"""
import logging

from app.core.exceptions import AppException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repo import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def register(self, req: RegisterRequest) -> TokenResponse:
        """Register a new user and return tokens."""
        existing = await self._repo.get_by_email(req.email)
        if existing:
            raise AppException(
                status_code=409,
                error_code="EMAIL_ALREADY_REGISTERED",
                message="An account with this email already exists.",
            )

        hashed = hash_password(req.password)
        user_id = await self._repo.create(
            email=req.email,
            full_name=req.full_name,
            hashed_password=hashed,
        )

        user_doc = await self._repo.get_by_id(user_id)
        logger.info("User registered", extra={"user_id": user_id, "email": req.email})
        return _build_token_response(user_doc)

    async def login(self, req: LoginRequest) -> TokenResponse:
        """Authenticate a user and return tokens."""
        user_doc = await self._repo.get_by_email(req.email)

        # Use constant-time comparison even if user doesn't exist
        dummy_hash = "$2b$12$dummy.hash.to.prevent.timing.attacks.padding.here.xxx"
        stored_hash = user_doc["hashed_password"] if user_doc else dummy_hash

        if not verify_password(req.password, stored_hash) or not user_doc:
            raise AppException(
                status_code=401,
                error_code="INVALID_CREDENTIALS",
                message="Incorrect email or password.",
            )

        if not user_doc.get("is_active", True):
            raise AppException(
                status_code=403,
                error_code="ACCOUNT_DISABLED",
                message="This account has been disabled.",
            )

        logger.info("User logged in", extra={"user_id": user_doc["_id"]})
        return _build_token_response(user_doc)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token using a valid refresh token."""
        try:
            user_id = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise AppException(
                status_code=401,
                error_code="INVALID_REFRESH_TOKEN",
                message=str(exc),
            )

        user_doc = await self._repo.get_by_id(user_id)
        if not user_doc or not user_doc.get("is_active", True):
            raise AppException(
                status_code=401,
                error_code="INVALID_REFRESH_TOKEN",
                message="User not found or inactive.",
            )

        return _build_token_response(user_doc)

    async def get_current_user(self, user_id: str) -> dict:
        """Resolve a user document from a decoded token subject."""
        user_doc = await self._repo.get_by_id(user_id)
        if not user_doc or not user_doc.get("is_active", True):
            raise AppException(
                status_code=401,
                error_code="USER_NOT_FOUND",
                message="User account not found or inactive.",
            )
        return user_doc


def _build_token_response(user_doc: dict) -> TokenResponse:
    user_id = user_doc["_id"]
    return TokenResponse(
        access_token=create_access_token(user_id, user_doc["email"]),
        refresh_token=create_refresh_token(user_id),
        user=UserResponse(
            id=user_id,
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            created_at=user_doc["created_at"],
        ),
    )
