"""
Interview service — generates a new interview with the 40/60 question mix.
"""
import logging

from app.core.exceptions import JDNotFoundException, ResumeNotFoundException
from app.models.session import InterviewQuestion
from app.repositories.jd_repo import JDRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.session_repo import SessionRepository
from app.schemas.session import GenerateInterviewRequest, GenerateInterviewResponse
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)


class InterviewService:
    def __init__(
        self,
        session_repo: SessionRepository,
        resume_repo: ResumeRepository,
        jd_repo: JDRepository,
        question_svc: QuestionService,
    ) -> None:
        self._session_repo = session_repo
        self._resume_repo = resume_repo
        self._jd_repo = jd_repo
        self._question_svc = question_svc

    async def generate_interview(
        self, request: GenerateInterviewRequest, user_id: str
    ) -> GenerateInterviewResponse:
        """
        Generate an interview session with mixed questions.
        Validates resume and JD exist before generating.
        """
        # Validate source documents exist
        resume_doc = await self._resume_repo.get_by_id(request.resume_id)
        if not resume_doc:
            raise ResumeNotFoundException(details={"resume_id": request.resume_id})

        jd_doc = await self._jd_repo.get_by_id(request.jd_id)
        if not jd_doc:
            raise JDNotFoundException(details={"jd_id": request.jd_id})

        resume_data = resume_doc.get("parsed_data", {})
        jd_data = jd_doc.get("parsed_data", {})

        # Generate mixed question set
        raw_questions = await self._question_svc.generate_interview_questions(
            resume_data=resume_data,
            jd_data=jd_data,
            interview_type=request.interview_type,
            total_count=request.question_count,
        )

        questions = [InterviewQuestion(**q) for q in raw_questions]

        # Persist session document
        doc = {
            "user_id": user_id,
            "resume_id": request.resume_id,
            "jd_id": request.jd_id,
            "interview_type": request.interview_type,
            "status": "created",
            "questions": [q.model_dump() for q in questions],
            "question_count": len(questions),
        }
        session_id = await self._session_repo.create(doc)

        session = await self._session_repo.get_by_id(session_id)

        logger.info(
            "Interview generated",
            extra={
                "session_id": session_id,
                "interview_type": request.interview_type,
                "question_count": len(questions),
            },
        )

        return GenerateInterviewResponse(
            session_id=session_id,
            interview_type=request.interview_type,
            question_count=len(questions),
            questions=questions,
            status="created",
            created_at=session["created_at"],
        )
