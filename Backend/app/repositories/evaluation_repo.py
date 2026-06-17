"""Evaluation repository."""
from datetime import datetime, UTC
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class EvaluationRepository(BaseRepository):
    collection_name = "evaluations"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def create(self, document: dict[str, Any]) -> str:
        document["evaluated_at"] = datetime.now(UTC)
        return await self.insert_one(document)

    async def get_by_answer_id(self, answer_id: str) -> dict[str, Any] | None:
        return await self.find_one({"answer_id": answer_id})

    async def get_by_session(self, session_id: str) -> list[dict[str, Any]]:
        return await self.find_many(
            {"session_id": session_id},
            sort=[("evaluated_at", 1)],
        )

    async def get_scores_by_session(self, session_id: str) -> list[dict[str, Any]]:
        """Return only score + category + question_category for aggregation."""
        pipeline = [
            {"$match": {"session_id": session_id}},
            {
                "$project": {
                    "score": 1,
                    "category_scores": 1,
                    "question_category": 1,
                    "answer_id": 1,
                }
            },
        ]
        return await self.aggregate(pipeline)
