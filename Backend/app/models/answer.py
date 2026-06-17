"""
Domain models for Answer and Evaluation.
"""
from datetime import datetime, UTC

from pydantic import BaseModel, Field


class AnswerDocument(BaseModel):
    id: str = Field(alias="_id", default="")
    session_id: str
    question_id: str
    question_text: str
    answer_text: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    time_taken_seconds: int = 0

    model_config = {"populate_by_name": True}


class CategoryScores(BaseModel):
    technical_accuracy: float = 0.0
    completeness: float = 0.0
    relevance: float = 0.0
    communication: float = 0.0


class AnswerFeedback(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    areas_for_improvement: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class EvaluationDocument(BaseModel):
    id: str = Field(alias="_id", default="")
    session_id: str
    answer_id: str
    question_text: str
    answer_text: str
    score: float = 0.0
    category_scores: CategoryScores = Field(default_factory=CategoryScores)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_points: list[str] = Field(default_factory=list)
    summary: str = ""
    feedback: AnswerFeedback = Field(default_factory=AnswerFeedback)
    question_category: str = ""
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
