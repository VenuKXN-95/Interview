"""
User domain model.
"""
from pydantic import BaseModel, EmailStr, Field


class UserInDB(BaseModel):
    """Represents a user document stored in MongoDB."""
    id: str = Field(..., alias="_id")
    email: str
    full_name: str
    hashed_password: str
    is_active: bool = True

    model_config = {"populate_by_name": True}
