"""Answer repository."""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class AnswerRepository(BaseRepository):
    collection_name = "answers"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        document["submitted_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_id(self, answer_id: str) -> dict[str, Any] | None:
        return await self.find_by_id(answer_id)

    async def get_by_session(self, session_id: str) -> list[dict[str, Any]]:
        return await self.find_many(
            {"session_id": session_id},
            sort=[("submitted_at", 1)],
        )

    async def get_by_session_and_question(
        self, session_id: str, question_id: str
    ) -> dict[str, Any] | None:
        return await self.find_one(
            {"session_id": session_id, "question_id": question_id}
        )
