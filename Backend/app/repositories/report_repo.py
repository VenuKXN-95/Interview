"""Report repository."""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    collection_name = "reports"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        document["generated_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_session(self, session_id: str) -> dict[str, Any] | None:
        return await self.find_one({"session_id": session_id})

    async def update_pdf_path(self, report_id: str, pdf_path: str) -> None:
        await self.update_one(report_id, {"$set": {"pdf_path": pdf_path}})
