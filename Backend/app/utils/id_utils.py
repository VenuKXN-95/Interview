"""
ObjectId utilities for consistent ID handling between
MongoDB (BSON ObjectId) and Pydantic/JSON (string).
"""
from bson import ObjectId

from app.core.exceptions import InvalidIDException


def new_object_id() -> str:
    """Generate a new MongoDB ObjectId as a hex string."""
    return str(ObjectId())


def validate_object_id(id_str: str) -> ObjectId:
    """
    Validate and convert a hex string to ObjectId.
    Raises InvalidIDException if invalid.
    """
    try:
        return ObjectId(id_str)
    except Exception:
        raise InvalidIDException(
            message=f"'{id_str}' is not a valid ObjectId.",
            details={"id": id_str},
        )


def to_object_id(id_str: str) -> ObjectId:
    """Alias for validate_object_id — use in repository layers."""
    return validate_object_id(id_str)
