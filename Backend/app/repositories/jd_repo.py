"""
JD repository.
"""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class JDRepository(BaseRepository):
    collection_name = "job_descriptions"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        document["created_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_id(self, jd_id: str) -> dict[str, Any] | None:
        return await self.find_by_id(jd_id)
