"""
Session repository — all DB access for the interview_sessions collection.
"""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import DESCENDING

from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    collection_name = "interview_sessions"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        document["created_at"] = datetime.now(UTC)
        document["updated_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_id(self, session_id: str) -> dict[str, Any] | None:
        return await self.find_by_id(session_id)

    async def update_status(
        self, session_id: str, status: str, extra_fields: dict | None = None
    ) -> None:
        update_doc: dict[str, Any] = {
            "$set": {
                "status": status,
                "updated_at": datetime.now(UTC),
                **(extra_fields or {}),
            }
        }
        await self.update_one(session_id, update_doc)

    async def list_by_resume(self, resume_id: str) -> list[dict[str, Any]]:
        from bson import ObjectId
        return await self.find_many(
            {"resume_id": resume_id},
            sort=[("created_at", DESCENDING)],
        )

    async def list_by_user(self, user_id: str) -> list[dict[str, Any]]:
        return await self.find_many(
            {"user_id": user_id},
            sort=[("created_at", DESCENDING)],
        )
