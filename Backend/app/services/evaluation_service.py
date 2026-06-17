"""
Evaluation service — LLM-based answer evaluation orchestration.
Prevents duplicate evaluations via unique index on answer_id.
"""
import logging

from app.core.exceptions import DuplicateAnswerException, SessionNotRunningException
from app.llm.client import OpenRouterClient
from app.models.answer import AnswerFeedback, CategoryScores
from app.prompts import answer_evaluation as eval_prompt
from app.repositories.answer_repo import AnswerRepository
from app.repositories.evaluation_repo import EvaluationRepository
from app.services.feedback_service import FeedbackService
from app.utils.validators import clamp_score

logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(
        self,
        eval_repo: EvaluationRepository,
        answer_repo: AnswerRepository,
        llm: OpenRouterClient,
        feedback_svc: FeedbackService,
    ) -> None:
        self._eval_repo = eval_repo
        self._answer_repo = answer_repo
        self._llm = llm
        self._feedback_svc = feedback_svc

    async def evaluate_answer(
        self,
        answer_id: str,
        session_id: str,
        question_text: str,
        answer_text: str,
        interview_type: str,
        category: str = "",
    ) -> dict:
        """
        Evaluate a single answer using LLM.
        Returns the full evaluation dict including feedback.
        Raises DuplicateAnswerException if already evaluated.
        """
        # Check for duplicate
        existing = await self._eval_repo.get_by_answer_id(answer_id)
        if existing:
            raise DuplicateAnswerException(
                details={"answer_id": answer_id}
            )

        # LLM evaluation
        raw_eval = await self._llm_evaluate(
            question_text, answer_text, interview_type, category
        )

        # Generate coaching feedback
        raw_eval["question"] = question_text
        feedback = await self._feedback_svc.generate_answer_feedback(raw_eval)

        # Persist
        doc = {
            "session_id": session_id,
            "answer_id": answer_id,
            "question_text": question_text,
            "answer_text": answer_text,
            "score": raw_eval["score"],
            "category_scores": raw_eval.get("category_scores", {}),
            "strengths": raw_eval.get("strengths", []),
            "weaknesses": raw_eval.get("weaknesses", []),
            "missing_points": raw_eval.get("missing_points", []),
            "summary": raw_eval.get("summary", ""),
            "feedback": feedback.model_dump(),
            "question_category": category,
        }
        eval_id = await self._eval_repo.create(doc)
        doc["_id"] = eval_id
        return doc

    async def _llm_evaluate(
        self,
        question: str,
        answer: str,
        interview_type: str,
        category: str,
    ) -> dict:
        """Call LLM and parse evaluation response."""
        try:
            data = await self._llm.complete_json(
                user_prompt=eval_prompt.build_evaluation_prompt(
                    question, answer, interview_type, category
                ),
                system_prompt=eval_prompt.SYSTEM_PROMPT,
                temperature=0.2,
            )

            raw_score = float(data.get("score", 5))
            score = clamp_score(raw_score, 0.0, 10.0)

            raw_cat = data.get("category_scores", {})
            category_scores = {
                "technical_accuracy": clamp_score(float(raw_cat.get("technical_accuracy", 5))),
                "completeness": clamp_score(float(raw_cat.get("completeness", 5))),
                "relevance": clamp_score(float(raw_cat.get("relevance", 5))),
                "communication": clamp_score(float(raw_cat.get("communication", 5))),
            }

            return {
                "score": score,
                "category_scores": category_scores,
                "strengths": data.get("strengths", []),
                "weaknesses": data.get("weaknesses", []),
                "missing_points": data.get("missing_points", []),
                "summary": data.get("summary", ""),
                "feedback": data.get("feedback", {}),
            }

        except Exception as exc:
            logger.error("LLM evaluation failed: %s — using fallback score 5", exc)
            return {
                "score": 5.0,
                "category_scores": {
                    "technical_accuracy": 5.0,
                    "completeness": 5.0,
                    "relevance": 5.0,
                    "communication": 5.0,
                },
                "strengths": [],
                "weaknesses": ["Evaluation service was unavailable."],
                "missing_points": [],
                "summary": "Automatic evaluation was unavailable. Score defaulted to 5.",
                "feedback": {
                    "strengths": [],
                    "areas_for_improvement": ["Evaluation service was unavailable."],
                    "recommendations": ["Review the topic and practice similar questions."],
                },
            }
