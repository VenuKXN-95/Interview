"""
Unit tests for Score Engine.
"""
import pytest
from unittest.mock import AsyncMock

from app.services.score_service import ScoreService, _get_recommendation, _weighted_avg


class TestWeightedAvg:
    def test_simple_average(self):
        assert _weighted_avg([6.0, 8.0]) == pytest.approx(7.0)

    def test_empty_list_returns_five(self):
        assert _weighted_avg([]) == 5.0

    def test_clamped_above_ten(self):
        result = _weighted_avg([12.0, 11.0])
        assert result <= 10.0

    def test_clamped_below_zero(self):
        result = _weighted_avg([-1.0, -2.0])
        assert result >= 0.0


class TestRecommendation:
    def test_strong_hire(self):
        assert _get_recommendation(9.0) == "strong_hire"
        assert _get_recommendation(10.0) == "strong_hire"

    def test_hire(self):
        assert _get_recommendation(7.5) == "hire"
        assert _get_recommendation(7.0) == "hire"

    def test_maybe(self):
        assert _get_recommendation(6.0) == "maybe"
        assert _get_recommendation(5.5) == "maybe"

    def test_no_hire(self):
        assert _get_recommendation(5.0) == "no_hire"
        assert _get_recommendation(0.0) == "no_hire"


class TestScoreService:
    @pytest.mark.asyncio
    async def test_empty_evaluations(self):
        mock_repo = AsyncMock()
        mock_repo.get_scores_by_session.return_value = []
        svc = ScoreService(mock_repo)
        result = await svc.calculate_scores("session123")
        assert result.overall_score == 0
        assert result.recommendation == "no_hire"

    @pytest.mark.asyncio
    async def test_high_scores_strong_hire(self):
        mock_repo = AsyncMock()
        mock_repo.get_scores_by_session.return_value = [
            {
                "score": 9.0,
                "category_scores": {
                    "technical_accuracy": 9,
                    "completeness": 9,
                    "relevance": 9,
                    "communication": 9,
                },
                "question_category": "Technical",
            }
        ] * 5
        svc = ScoreService(mock_repo)
        result = await svc.calculate_scores("session123")
        assert result.overall_score >= 8.5
        assert result.recommendation == "strong_hire"

    @pytest.mark.asyncio
    async def test_low_scores_no_hire(self):
        mock_repo = AsyncMock()
        mock_repo.get_scores_by_session.return_value = [
            {
                "score": 3.0,
                "category_scores": {
                    "technical_accuracy": 3,
                    "completeness": 3,
                    "relevance": 3,
                    "communication": 3,
                },
                "question_category": "Behavioral",
            }
        ] * 5
        svc = ScoreService(mock_repo)
        result = await svc.calculate_scores("session123")
        assert result.overall_score < 5.5
        assert result.recommendation == "no_hire"
