"""
FastAPI dependency injection wiring.
All dependencies are defined here and imported into route files.
Services and repositories are constructed per-request via Depends().
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.security import decode_access_token
from app.database.mongodb import get_database

# OAuth2 scheme — reads Bearer token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# ── Database ─────────────────────────────────────────────────
DBDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]


# ── Repositories ─────────────────────────────────────────────
def get_resume_repo(db: DBDep):
    from app.repositories.resume_repo import ResumeRepository
    return ResumeRepository(db)


def get_jd_repo(db: DBDep):
    from app.repositories.jd_repo import JDRepository
    return JDRepository(db)


def get_question_repo(db: DBDep):
    from app.repositories.question_repo import QuestionRepository
    return QuestionRepository(db)


def get_session_repo(db: DBDep):
    from app.repositories.session_repo import SessionRepository
    return SessionRepository(db)


def get_answer_repo(db: DBDep):
    from app.repositories.answer_repo import AnswerRepository
    return AnswerRepository(db)


def get_evaluation_repo(db: DBDep):
    from app.repositories.evaluation_repo import EvaluationRepository
    return EvaluationRepository(db)


def get_report_repo(db: DBDep):
    from app.repositories.report_repo import ReportRepository
    return ReportRepository(db)


# ── LLM Client ───────────────────────────────────────────────
def get_llm_client():
    from app.llm.client import OpenRouterClient
    return OpenRouterClient()


# ── Auth Dependencies ─────────────────────────────────────────
def get_user_repo(db: DBDep):
    from app.repositories.user_repo import UserRepository
    return UserRepository(db)


def get_auth_service(repo=Depends(get_user_repo)):
    from app.services.auth_service import AuthService
    return AuthService(repo)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DBDep,
) -> dict:
    """FastAPI dependency — decodes JWT and returns the current user dict."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload["sub"]
    except ValueError:
        raise credentials_exc

    from app.repositories.user_repo import UserRepository
    user_doc = await UserRepository(db).get_by_id(user_id)
    if not user_doc or not user_doc.get("is_active", True):
        raise credentials_exc
    return user_doc


# Convenience type alias for route handlers
CurrentUser = Annotated[dict, Depends(get_current_user)]


# ── Services ─────────────────────────────────────────────────
def get_resume_service(
    repo=Depends(get_resume_repo),
    llm=Depends(get_llm_client),
):
    from app.services.resume_service import ResumeService
    return ResumeService(repo, llm)


def get_jd_service(
    repo=Depends(get_jd_repo),
    llm=Depends(get_llm_client),
):
    from app.services.jd_service import JDService
    return JDService(repo, llm)


def get_question_service(
    q_repo=Depends(get_question_repo),
    llm=Depends(get_llm_client),
):
    from app.services.question_service import QuestionService
    return QuestionService(q_repo, llm)


def get_interview_service(
    session_repo=Depends(get_session_repo),
    resume_repo=Depends(get_resume_repo),
    jd_repo=Depends(get_jd_repo),
    question_svc=Depends(get_question_service),
):
    from app.services.interview_service import InterviewService
    return InterviewService(session_repo, resume_repo, jd_repo, question_svc)


def get_session_service(repo=Depends(get_session_repo)):
    from app.services.session_service import SessionService
    return SessionService(repo)


def get_feedback_service(llm=Depends(get_llm_client)):
    from app.services.feedback_service import FeedbackService
    return FeedbackService(llm)


def get_evaluation_service(
    eval_repo=Depends(get_evaluation_repo),
    answer_repo=Depends(get_answer_repo),
    llm=Depends(get_llm_client),
    feedback_svc=Depends(get_feedback_service),
):
    from app.services.evaluation_service import EvaluationService
    return EvaluationService(eval_repo, answer_repo, llm, feedback_svc)


def get_score_service(eval_repo=Depends(get_evaluation_repo)):
    from app.services.score_service import ScoreService
    return ScoreService(eval_repo)


def get_answer_service(
    answer_repo=Depends(get_answer_repo),
    session_repo=Depends(get_session_repo),
    eval_svc=Depends(get_evaluation_service),
):
    from app.services.answer_service import AnswerService
    return AnswerService(answer_repo, session_repo, eval_svc)


def get_report_service(
    report_repo=Depends(get_report_repo),
    session_repo=Depends(get_session_repo),
    answer_repo=Depends(get_answer_repo),
    eval_repo=Depends(get_evaluation_repo),
    score_svc=Depends(get_score_service),
):
    from app.services.report_service import ReportService
    return ReportService(report_repo, session_repo, answer_repo, eval_repo, score_svc)
