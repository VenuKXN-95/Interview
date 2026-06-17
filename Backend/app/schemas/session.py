"""
Pydantic V2 schemas for Interview Generation and Session APIs.
"""
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.models.session import InterviewQuestion, InterviewType, SessionStatus


# ── Interview Generation ──────────────────────────────────────

class GenerateInterviewRequest(BaseModel):
    resume_id: str = Field(..., description="ObjectId of the uploaded resume")
    jd_id: str = Field(..., description="ObjectId of the uploaded job description")
    interview_type: InterviewType = Field(..., description="Type of interview")
    question_count: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Total number of questions (5-20)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "665f1a2b3c4d5e6f7a8b9c0d",
                "jd_id": "665f1a2b3c4d5e6f7a8b9c0e",
                "interview_type": "technical",
                "question_count": 10,
            }
        }
    }


class GenerateInterviewResponse(BaseModel):
    session_id: str
    interview_type: InterviewType
    question_count: int
    questions: list[InterviewQuestion]
    status: SessionStatus
    created_at: datetime


# ── Session ───────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str
    resume_id: str
    jd_id: str
    interview_type: InterviewType
    status: SessionStatus
    question_count: int
    questions: list[InterviewQuestion]
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    updated_at: datetime
