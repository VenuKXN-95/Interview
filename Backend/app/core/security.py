"""
Security utilities — password hashing and JWT token operations.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Password Hashing ──────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the plain-text password."""
    pwd_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the bcrypt hash."""
    pwd_bytes = plain.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


# ── JWT Token Creation ────────────────────────────────────────

def _build_token(data: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    payload["iat"] = datetime.now(timezone.utc)
    payload["type"] = token_type
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, email: str) -> str:
    """Create a short-lived access token."""
    return _build_token(
        data={"sub": user_id, "email": email},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
        token_type="access",
    )


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token."""
    return _build_token(
        data={"sub": user_id},
        expires_delta=timedelta(days=settings.jwt_refresh_token_expire_days),
        token_type="refresh",
    )


# ── JWT Token Decoding ────────────────────────────────────────

def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate an access token.
    Raises ValueError with a user-friendly message on any failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError(f"Invalid or expired token: {exc}") from exc

    if payload.get("type") != "access":
        raise ValueError("Token is not an access token.")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Token missing subject claim.")

    return payload


def decode_refresh_token(token: str) -> str:
    """
    Decode a refresh token and return the user_id (sub).
    Raises ValueError on failure.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError(f"Invalid or expired refresh token: {exc}") from exc

    if payload.get("type") != "refresh":
        raise ValueError("Token is not a refresh token.")

    user_id = payload.get("sub")
    if not user_id:
        raise ValueError("Refresh token missing subject claim.")

    return user_id
