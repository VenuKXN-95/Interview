"""
Report service — orchestrates scoring, session feedback generation, and PDF creation.
"""
import logging
import os
from datetime import datetime
from pathlib import Path

from app.core.exceptions import ReportNotFoundException, SessionNotFoundException
from app.repositories.answer_repo import AnswerRepository
from app.repositories.evaluation_repo import EvaluationRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.session_repo import SessionRepository
from app.reports.builder import build_report_pdf
from app.services.score_service import ScoreService
from app.services.feedback_service import FeedbackService
from app.utils.file_utils import ensure_reports_dir

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(
        self,
        report_repo: ReportRepository,
        session_repo: SessionRepository,
        answer_repo: AnswerRepository,
        eval_repo: EvaluationRepository,
        score_svc: ScoreService,
    ) -> None:
        self._report_repo = report_repo
        self._session_repo = session_repo
        self._answer_repo = answer_repo
        self._eval_repo = eval_repo
        self._score_svc = score_svc

    async def get_or_generate_report(self, session_id: str) -> str:
        """
        Return path to existing PDF or generate a new one.
        Reports are cached — one per session.
        """
        # Check cached report
        existing = await self._report_repo.get_by_session(session_id)
        if existing and existing.get("pdf_path") and os.path.exists(existing["pdf_path"]):
            logger.info("Returning cached report", extra={"session_id": session_id})
            return existing["pdf_path"]

        # Generate new report
        return await self._generate_report(session_id, existing)

    async def get_report_json(self, session_id: str) -> dict:
        """Return the report data as a dict (no PDF)."""
        existing = await self._report_repo.get_by_session(session_id)
        if not existing:
            logger.info("Report not found for session %s, generating it on the fly", session_id)
            await self._generate_report(session_id, None)
            existing = await self._report_repo.get_by_session(session_id)
            if not existing:
                raise ReportNotFoundException(details={"session_id": session_id})
        return existing

    async def _generate_report(self, session_id: str, existing_doc: dict | None) -> str:
        session = await self._session_repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundException(details={"session_id": session_id})

        answers = await self._answer_repo.get_by_session(session_id)
        evaluations = await self._eval_repo.get_by_session(session_id)

        # Build answer→evaluation map
        eval_map = {e["answer_id"]: e for e in evaluations}

        # Score calculation
        scores = await self._score_svc.calculate_scores(session_id)

        # Session feedback via LLM
        session_feedback: dict = {}
        if evaluations:
            try:
                from app.llm.client import OpenRouterClient
                from app.services.feedback_service import FeedbackService
                fb_svc = FeedbackService(OpenRouterClient())
                session_feedback = await fb_svc.generate_session_feedback(
                    session_evaluations=evaluations,
                    interview_type=session.get("interview_type", "hr"),
                    overall_score=scores.overall_score,
                )
            except Exception as exc:
                logger.warning("Session feedback failed: %s", exc)

        # Build Q&A list for PDF
        qa_list = _build_qa_list(session, answers, eval_map)

        # Candidate name from first answer's context or session
        candidate_name = _extract_candidate_name(session)

        report_data = {
            "candidate_name": candidate_name,
            "interview_type": session.get("interview_type", ""),
            "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "total_questions": session.get("question_count", 0),
            "answered_questions": len(answers),
            "scores": scores.to_dict(),
            "recommendation": scores.recommendation,
            "session_feedback": session_feedback,
            "questions_and_answers": qa_list,
        }

        # Generate PDF
        reports_dir = ensure_reports_dir()
        pdf_path = str(reports_dir / f"report_{session_id}.pdf")
        build_report_pdf(pdf_path, report_data)

        # Persist or update report record
        report_doc = {
            "session_id": session_id,
            "resume_id": session.get("resume_id", ""),
            "jd_id": session.get("jd_id", ""),
            "candidate_name": candidate_name,
            "interview_type": session.get("interview_type", ""),
            "scores": scores.to_dict(),
            "recommendation": scores.recommendation,
            "session_feedback": session_feedback,
            "total_questions": session.get("question_count", 0),
            "answered_questions": len(answers),
            "pdf_path": pdf_path,
        }

        if existing_doc:
            await self._report_repo.update_one(
                existing_doc["_id"], {"$set": {**report_doc, "generated_at": datetime.utcnow()}}
            )
        else:
            await self._report_repo.create(report_doc)

        logger.info(
            "Report generated",
            extra={
                "session_id": session_id,
                "overall_score": scores.overall_score,
                "recommendation": scores.recommendation,
                "pdf_path": pdf_path,
            },
        )
        return pdf_path


def _build_qa_list(session: dict, answers: list[dict], eval_map: dict) -> list[dict]:
    """Build ordered Q&A+evaluation list for the PDF."""
    question_map = {q["question_id"]: q for q in session.get("questions", [])}
    answer_by_qid = {a["question_id"]: a for a in answers}

    result = []
    for q in sorted(session.get("questions", []), key=lambda x: x.get("order", 0)):
        qid = q["question_id"]
        answer = answer_by_qid.get(qid)
        if answer:
            eval_doc = eval_map.get(answer["_id"], {})
            result.append({
                "question": q.get("question_text", ""),
                "category": q.get("category", ""),
                "difficulty": q.get("difficulty", ""),
                "answer": answer.get("answer_text", ""),
                "score": eval_doc.get("score", 0),
                "evaluation": eval_doc,
            })
        else:
            result.append({
                "question": q.get("question_text", ""),
                "category": q.get("category", ""),
                "difficulty": q.get("difficulty", ""),
                "answer": None,
                "score": 0,
                "evaluation": {},
            })
    return result


def _extract_candidate_name(session: dict) -> str:
    """Best-effort candidate name extraction."""
    return session.get("candidate_name", "Candidate")
