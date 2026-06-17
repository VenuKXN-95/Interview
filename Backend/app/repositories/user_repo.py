"""
User repository — MongoDB CRUD for the users collection.
"""
import logging
from datetime import datetime, timezone

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db["users"]

    async def create(self, email: str, full_name: str, hashed_password: str) -> str:
        """Insert a new user. Returns the new user's string ID."""
        doc = {
            "email": email.lower().strip(),
            "full_name": full_name.strip(),
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self._col.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_email(self, email: str) -> dict | None:
        """Find a user by email (case-insensitive)."""
        doc = await self._col.find_one({"email": email.lower().strip()})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def get_by_id(self, user_id: str) -> dict | None:
        """Find a user by MongoDB ObjectId string."""
        try:
            doc = await self._col.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc
