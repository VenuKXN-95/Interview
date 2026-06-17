"""
Resume repository — all DB access for the resumes collection.
"""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository):
    collection_name = "resumes"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        """Insert a resume document and return its id."""
        document["created_at"] = datetime.now(UTC)
        document["updated_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_id(self, resume_id: str) -> dict[str, Any] | None:
        return await self.find_by_id(resume_id)
