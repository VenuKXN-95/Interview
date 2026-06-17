"""
Answer service — handles submission, validation, and evaluation triggering.
"""
import logging

from app.core.exceptions import (
    DuplicateAnswerException,
    SessionNotRunningException,
    SessionNotFoundException,
)
from app.models.answer import AnswerFeedback, CategoryScores
from app.repositories.answer_repo import AnswerRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.answer import EvaluationResult, SubmitAnswerRequest, SubmitAnswerResponse
from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(
        self,
        answer_repo: AnswerRepository,
        session_repo: SessionRepository,
        eval_svc: EvaluationService,
    ) -> None:
        self._answer_repo = answer_repo
        self._session_repo = session_repo
        self._eval_svc = eval_svc

    async def submit_answer(self, request: SubmitAnswerRequest) -> SubmitAnswerResponse:
        """
        Submit an answer:
          1. Validate session exists and is running
          2. Check no duplicate answer for this question
          3. Persist the answer
          4. Trigger synchronous LLM evaluation
          5. Return evaluation result
        """
        # Validate session
        session = await self._session_repo.get_by_id(request.session_id)
        if not session:
            raise SessionNotFoundException(details={"session_id": request.session_id})
        if session["status"] != "running":
            raise SessionNotRunningException(
                message=f"Session is in '{session['status']}' state. Must be 'running' to accept answers.",
                details={"session_id": request.session_id, "status": session["status"]},
            )

        # Check duplicate
        existing = await self._answer_repo.get_by_session_and_question(
            request.session_id, request.question_id
        )
        if existing:
            raise DuplicateAnswerException(
                message="An answer has already been submitted for this question in this session.",
                details={
                    "session_id": request.session_id,
                    "question_id": request.question_id,
                },
            )

        # Find question category from session
        question_category = _get_question_category(session, request.question_id)
        interview_type = session.get("interview_type", "hr")

        # Persist answer
        answer_doc = {
            "session_id": request.session_id,
            "question_id": request.question_id,
            "question_text": request.question_text,
            "answer_text": request.answer_text,
            "time_taken_seconds": request.time_taken_seconds,
        }
        answer_id = await self._answer_repo.create(answer_doc)

        # Evaluate
        eval_doc = await self._eval_svc.evaluate_answer(
            answer_id=answer_id,
            session_id=request.session_id,
            question_text=request.question_text,
            answer_text=request.answer_text,
            interview_type=interview_type,
            category=question_category,
        )

        answer = await self._answer_repo.get_by_id(answer_id)

        cat_scores = eval_doc.get("category_scores", {})
        feedback_data = eval_doc.get("feedback", {})

        return SubmitAnswerResponse(
            answer_id=answer_id,
            session_id=request.session_id,
            question_id=request.question_id,
            evaluation=EvaluationResult(
                score=eval_doc["score"],
                category_scores=CategoryScores(**cat_scores),
                strengths=eval_doc.get("strengths", []),
                weaknesses=eval_doc.get("weaknesses", []),
                missing_points=eval_doc.get("missing_points", []),
                summary=eval_doc.get("summary", ""),
                feedback=AnswerFeedback(**feedback_data),
            ),
            submitted_at=answer["submitted_at"],
        )

    async def get_session_answers(self, session_id: str) -> list[dict]:
        return await self._answer_repo.get_by_session(session_id)


def _get_question_category(session: dict, question_id: str) -> str:
    """Extract question category from session document."""
    for q in session.get("questions", []):
        if q.get("question_id") == question_id:
            return q.get("category", "")
    return ""
