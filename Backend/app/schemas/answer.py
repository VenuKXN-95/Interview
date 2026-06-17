"""
Pydantic V2 schemas for Answer and Evaluation APIs.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.answer import AnswerFeedback, CategoryScores


class SubmitAnswerRequest(BaseModel):
    session_id: str = Field(..., description="Session ObjectId")
    question_id: str = Field(..., description="Question ID (from session questions list)")
    question_text: str = Field(..., min_length=5, description="The question text")
    answer_text: str = Field(
        ..., min_length=1, max_length=5000, description="Candidate's answer"
    )
    time_taken_seconds: int = Field(default=0, ge=0, description="Time spent on this answer")

    model_config = {
        "json_schema_extra": {
            "example": {
                "session_id": "665f1a2b3c4d5e6f7a8b9c0d",
                "question_id": "ai_0",
                "question_text": "Explain how you would design a rate limiter.",
                "answer_text": "I would use a token bucket algorithm...",
                "time_taken_seconds": 120,
            }
        }
    }


class EvaluationResult(BaseModel):
    score: float = Field(..., ge=0, le=10)
    category_scores: CategoryScores
    strengths: list[str]
    weaknesses: list[str]
    missing_points: list[str]
    summary: str
    feedback: AnswerFeedback


class SubmitAnswerResponse(BaseModel):
    answer_id: str
    session_id: str
    question_id: str
    evaluation: EvaluationResult
    submitted_at: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer_id": "665f...",
                "session_id": "665f...",
                "question_id": "ai_0",
                "evaluation": {
                    "score": 7.5,
                    "category_scores": {
                        "technical_accuracy": 8,
                        "completeness": 7,
                        "relevance": 9,
                        "communication": 6,
                    },
                    "strengths": ["Good understanding of token bucket algorithm"],
                    "weaknesses": ["Did not mention distributed implementation"],
                    "missing_points": ["Redis-based implementation", "sliding window alternative"],
                    "summary": "Solid answer showing good conceptual understanding.",
                    "feedback": {
                        "strengths": ["Clear explanation of core algorithm"],
                        "areas_for_improvement": ["Consider distributed scenarios"],
                        "recommendations": ["Study Redis-based rate limiting implementations"],
                    },
                },
                "submitted_at": "2026-01-01T10:00:00",
            }
        }
    }


class AnswerListResponse(BaseModel):
    session_id: str
    answers: list[SubmitAnswerResponse]
    total: int
