"""
Domain model for Question Bank entries.
"""
from typing import Literal

from pydantic import BaseModel, Field


InterviewType = Literal["hr", "technical", "telephonic", "virtual"]
Difficulty = Literal["easy", "medium", "hard"]


class QuestionDocument(BaseModel):
    id: str = Field(alias="_id", default="")
    interview_type: InterviewType
    category: str
    difficulty: Difficulty
    question: str
    tags: list[str] = Field(default_factory=list)
    is_active: bool = True

    model_config = {"populate_by_name": True}
