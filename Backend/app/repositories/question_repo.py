"""
Question repository.
Supports random sampling by interview_type and difficulty (uses compound index).
"""
import random
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.repositories.base import BaseRepository


class QuestionRepository(BaseRepository):
    collection_name = "question_bank"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db)

    async def get_random_sample(
        self,
        interview_type: str,
        count: int,
        difficulty_mix: dict[str, int] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Pull `count` questions for the given interview_type.
        difficulty_mix: {"easy": n, "medium": n, "hard": n}
        If not specified, pulls `count` random questions across all difficulties.
        Uses $sample aggregation for true random selection.
        """
        if not difficulty_mix:
            pipeline = [
                {"$match": {"interview_type": interview_type, "is_active": True}},
                {"$sample": {"size": count}},
            ]
            return await self.aggregate(pipeline)

        results: list[dict[str, Any]] = []
        for difficulty, n in difficulty_mix.items():
            if n <= 0:
                continue
            pipeline = [
                {
                    "$match": {
                        "interview_type": interview_type,
                        "difficulty": difficulty,
                        "is_active": True,
                    }
                },
                {"$sample": {"size": n}},
            ]
            results.extend(await self.aggregate(pipeline))

        random.shuffle(results)
        return results[:count]

    async def get_by_tags(
        self, tags: list[str], interview_type: str, count: int = 5
    ) -> list[dict[str, Any]]:
        """Pull questions matching candidate skill tags."""
        pipeline = [
            {
                "$match": {
                    "interview_type": interview_type,
                    "tags": {"$in": tags},
                    "is_active": True,
                }
            },
            {"$sample": {"size": count}},
        ]
        return await self.aggregate(pipeline)

    async def insert_many_questions(self, questions: list[dict[str, Any]]) -> int:
        result = await self._col.insert_many(questions)
        return len(result.inserted_ids)

    async def get_count_by_type(self, interview_type: str) -> int:
        return await self.count({"interview_type": interview_type, "is_active": True})
