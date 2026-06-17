"""
Feedback service — generates per-answer and session-level coaching feedback.
"""
import logging

from app.llm.client import OpenRouterClient
from app.models.answer import AnswerFeedback
from app.prompts import feedback_generation as fb_prompt

logger = logging.getLogger(__name__)


class FeedbackService:
    def __init__(self, llm: OpenRouterClient) -> None:
        self._llm = llm

    async def generate_answer_feedback(
        self,
        evaluation_summary: dict,
    ) -> AnswerFeedback:
        """Generate coaching feedback for a single answer evaluation."""
        try:
            # Check if feedback is already provided to avoid double LLM calls
            if "feedback" in evaluation_summary and isinstance(evaluation_summary["feedback"], dict):
                fb = evaluation_summary["feedback"]
                # Only use if it actually has content to be safe
                if fb.get("strengths") or fb.get("areas_for_improvement") or fb.get("recommendations"):
                    logger.info("Using pre-generated coaching feedback from evaluation response.")
                    return AnswerFeedback(
                        strengths=fb.get("strengths", []),
                        areas_for_improvement=fb.get("areas_for_improvement", []),
                        recommendations=fb.get("recommendations", []),
                    )

            data = await self._llm.complete_json(
                user_prompt=fb_prompt.build_feedback_prompt(evaluation_summary),
                system_prompt=fb_prompt.SYSTEM_PROMPT,
                temperature=0.5,
            )
            return AnswerFeedback(
                strengths=data.get("strengths", []),
                areas_for_improvement=data.get("areas_for_improvement", []),
                recommendations=data.get("recommendations", []),
            )
        except Exception as exc:
            logger.warning("Feedback generation failed: %s — using defaults", exc)
            return AnswerFeedback(
                strengths=evaluation_summary.get("strengths", []),
                areas_for_improvement=evaluation_summary.get("weaknesses", []),
                recommendations=["Review the topic and practice similar questions."],
            )

    async def generate_session_feedback(
        self,
        session_evaluations: list[dict],
        interview_type: str,
        overall_score: float,
    ) -> dict:
        """Generate comprehensive session-level feedback."""
        try:
            data = await self._llm.complete_json(
                user_prompt=fb_prompt.build_session_feedback_prompt(
                    session_evaluations, interview_type, overall_score
                ),
                system_prompt=fb_prompt.SYSTEM_PROMPT,
                temperature=0.5,
            )
            return data
        except Exception as exc:
            logger.warning("Session feedback generation failed: %s", exc)
            return {
                "overall_assessment": f"Overall score: {overall_score:.1f}/10.",
                "key_strengths": [],
                "priority_improvements": [],
                "interview_readiness": "needs_preparation" if overall_score < 6 else "almost_ready",
                "next_steps": ["Practice more mock interviews.", "Review areas with low scores."],
            }
