"""
Unit tests for Evaluation Service.
"""
import pytest
from unittest.mock import AsyncMock

from app.services.evaluation_service import EvaluationService
from app.services.feedback_service import FeedbackService
from app.models.answer import AnswerFeedback
from app.core.exceptions import DuplicateAnswerException


class TestEvaluationService:
    def _make_svc(self, mock_llm, existing_eval=None):
        eval_repo = AsyncMock()
        eval_repo.get_by_answer_id.return_value = existing_eval
        eval_repo.create.return_value = "eval_id_123"

        answer_repo = AsyncMock()
        fb_svc = AsyncMock(spec=FeedbackService)
        fb_svc.generate_answer_feedback.return_value = AnswerFeedback(
            strengths=["Good point"],
            areas_for_improvement=["Add more detail"],
            recommendations=["Study X"],
        )
        return EvaluationService(eval_repo, answer_repo, mock_llm, fb_svc)

    @pytest.mark.asyncio
    async def test_duplicate_raises(self, mock_eval_llm):
        # Simulate existing evaluation
        svc = self._make_svc(mock_eval_llm, existing_eval={"_id": "existing"})
        with pytest.raises(DuplicateAnswerException):
            await svc.evaluate_answer(
                "answer_123", "session_456", "What is DI?", "Dependency injection...", "technical"
            )

    @pytest.mark.asyncio
    async def test_evaluation_score_clamped(self, mock_eval_llm):
        # LLM returns score of 15 (out of range)
        mock_eval_llm.complete_json.return_value = {
            "score": 15,
            "category_scores": {"technical_accuracy": 15, "completeness": 5, "relevance": 5, "communication": 5},
            "strengths": [],
            "weaknesses": [],
            "missing_points": [],
            "summary": "Test",
        }
        svc = self._make_svc(mock_eval_llm)
        result = await svc.evaluate_answer(
            "a1", "s1", "Question?", "Answer.", "technical"
        )
        assert result["score"] <= 10.0

    @pytest.mark.asyncio
    async def test_evaluation_llm_failure_fallback(self):
        llm = AsyncMock()
        llm.complete_json.side_effect = Exception("LLM down")
        svc = self._make_svc(llm)
        result = await svc.evaluate_answer(
            "a1", "s1", "Question?", "Answer.", "technical"
        )
        # Should return fallback score of 5
        assert result["score"] == 5.0
