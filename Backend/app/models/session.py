"""
Domain models for Interview Session.
"""
from datetime import datetime, UTC
from typing import Literal

from pydantic import BaseModel, Field

InterviewType = Literal["hr", "technical", "telephonic", "virtual"]
SessionStatus = Literal["created", "running", "completed", "abandoned"]


class InterviewQuestion(BaseModel):
    question_id: str
    source: Literal["bank", "ai_generated", "generic"]
    question_text: str
    category: str = ""
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: list[str] = Field(default_factory=list)
    order: int = 0


class InterviewSession(BaseModel):
    id: str = Field(alias="_id", default="")
    resume_id: str
    jd_id: str
    interview_type: InterviewType
    status: SessionStatus = "created"
    questions: list[InterviewQuestion] = Field(default_factory=list)
    question_count: int = 10
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
