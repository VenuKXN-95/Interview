"""
Score Engine — calculates multi-dimensional scores from evaluation data.

Formula:
  technical_score       = weighted avg of technical_accuracy scores
  communication_score   = weighted avg of communication scores
  problem_solving_score = weighted avg of relevance + completeness (problem questions)
  project_score         = avg of scores for Project/Architecture questions

  overall_score = (
      technical_score      * 0.35 +
      communication_score  * 0.25 +
      problem_solving_score* 0.25 +
      project_score        * 0.15
  )

Recommendation:
  8.5–10.0 → strong_hire
  7.0–8.4  → hire
  5.5–6.9  → maybe
  0.0–5.4  → no_hire
"""
import logging
from typing import Literal

from app.repositories.evaluation_repo import EvaluationRepository
from app.utils.validators import clamp_score

logger = logging.getLogger(__name__)

Recommendation = Literal["strong_hire", "hire", "maybe", "no_hire"]


class ScoreResult:
    def __init__(
        self,
        technical_score: float,
        communication_score: float,
        problem_solving_score: float,
        project_score: float,
        overall_score: float,
        recommendation: Recommendation,
    ) -> None:
        self.technical_score = round(technical_score, 2)
        self.communication_score = round(communication_score, 2)
        self.problem_solving_score = round(problem_solving_score, 2)
        self.project_score = round(project_score, 2)
        self.overall_score = round(overall_score, 2)
        self.recommendation = recommendation

    def to_dict(self) -> dict:
        return {
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "problem_solving_score": self.problem_solving_score,
            "project_score": self.project_score,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
        }


class ScoreService:
    def __init__(self, eval_repo: EvaluationRepository) -> None:
        self._eval_repo = eval_repo

    async def calculate_scores(self, session_id: str) -> ScoreResult:
        """
        Compute all dimensional scores from session evaluations.
        Handles partial evaluations gracefully (some questions may not be answered).
        """
        evaluations = await self._eval_repo.get_scores_by_session(session_id)

        if not evaluations:
            logger.warning(
                "No evaluations found for scoring", extra={"session_id": session_id}
            )
            return ScoreResult(0, 0, 0, 0, 0, "no_hire")

        # Extract scores
        all_scores = [float(e.get("score", 0)) for e in evaluations]
        cat_scores = [e.get("category_scores", {}) for e in evaluations]
        categories = [e.get("question_category", "").lower() for e in evaluations]

        # Dimensional scores
        technical_score = _weighted_avg(
            [float(c.get("technical_accuracy", 5)) for c in cat_scores]
        )
        communication_score = _weighted_avg(
            [float(c.get("communication", 5)) for c in cat_scores]
        )
        problem_solving_score = _weighted_avg(
            [
                (float(c.get("relevance", 5)) + float(c.get("completeness", 5))) / 2
                for i, c in enumerate(cat_scores)
                if "problem" in categories[i] or "architecture" in categories[i]
            ]
            or [float(c.get("relevance", 5)) for c in cat_scores]
        )
        project_score = _category_avg(
            all_scores, categories, keywords=["project", "architecture", "design"]
        )

        # Overall score using weighted formula
        overall_score = clamp_score(
            technical_score      * 0.35
            + communication_score  * 0.25
            + problem_solving_score* 0.25
            + project_score        * 0.15,
            0.0,
            10.0,
        )

        recommendation = _get_recommendation(overall_score)

        logger.info(
            "Scores calculated",
            extra={
                "session_id": session_id,
                "overall": overall_score,
                "recommendation": recommendation,
            },
        )

        return ScoreResult(
            technical_score=technical_score,
            communication_score=communication_score,
            problem_solving_score=problem_solving_score,
            project_score=project_score,
            overall_score=overall_score,
            recommendation=recommendation,
        )


def _weighted_avg(scores: list[float]) -> float:
    """Simple mean, clamped to [0, 10]."""
    if not scores:
        return 5.0
    return clamp_score(sum(scores) / len(scores), 0.0, 10.0)


def _category_avg(
    all_scores: list[float],
    categories: list[str],
    keywords: list[str],
) -> float:
    """Average scores for questions matching specific category keywords."""
    relevant = [
        score
        for score, cat in zip(all_scores, categories)
        if any(kw in cat for kw in keywords)
    ]
    if not relevant:
        return _weighted_avg(all_scores)  # Fall back to overall avg
    return _weighted_avg(relevant)


def _get_recommendation(overall_score: float) -> Recommendation:
    if overall_score >= 8.5:
        return "strong_hire"
    elif overall_score >= 7.0:
        return "hire"
    elif overall_score >= 5.5:
        return "maybe"
    else:
        return "no_hire"
