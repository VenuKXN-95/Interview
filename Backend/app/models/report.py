"""
Domain model for Report.
"""
from datetime import datetime, UTC
from typing import Literal

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    technical_score: float = 0.0
    communication_score: float = 0.0
    problem_solving_score: float = 0.0
    project_score: float = 0.0
    overall_score: float = 0.0


class ReportDocument(BaseModel):
    id: str = Field(alias="_id", default="")
    session_id: str
    resume_id: str
    jd_id: str
    candidate_name: str = ""
    interview_type: str = ""
    scores: ScoreBreakdown
    recommendation: Literal["strong_hire", "hire", "maybe", "no_hire"]
    session_feedback: dict = Field(default_factory=dict)
    total_questions: int = 0
    answered_questions: int = 0
    pdf_path: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
