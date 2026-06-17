"""
Interview generation and session management routes.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, get_interview_service, get_session_service
from app.schemas.session import GenerateInterviewRequest, GenerateInterviewResponse, SessionResponse
from app.services.interview_service import InterviewService
from app.services.session_service import SessionService

router = APIRouter()


# ── Interview Generation ──────────────────────────────────────

@router.post(
    "/interview/generate",
    response_model=GenerateInterviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an interview with personalized questions",
    description=(
        "Creates an interview session with a mixed set of questions: "
        "40% from the curated question bank, 60% AI-generated based on resume + JD."
    ),
    responses={
        404: {"description": "Resume or JD not found"},
    },
)
async def generate_interview(
    body: GenerateInterviewRequest,
    service: Annotated[InterviewService, Depends(get_interview_service)],
    _user: CurrentUser,
) -> GenerateInterviewResponse:
    return await service.generate_interview(body)


@router.get(
    "/interview/{session_id}",
    response_model=GenerateInterviewResponse,
    summary="Get interview details by session ID",
)
async def get_interview(
    session_id: str,
    session_svc: Annotated[SessionService, Depends(get_session_service)],
    _user: CurrentUser,
) -> SessionResponse:
    return await session_svc.get_session(session_id)


# ── Session Lifecycle ─────────────────────────────────────────

@router.post(
    "/session/{session_id}/start",
    response_model=SessionResponse,
    summary="Start an interview session",
    description="Transitions session status from 'created' to 'running'.",
    responses={
        409: {"description": "Invalid state transition"},
        404: {"description": "Session not found"},
    },
)
async def start_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
    _user: CurrentUser,
) -> SessionResponse:
    return await service.start_session(session_id)


@router.post(
    "/session/{session_id}/end",
    response_model=SessionResponse,
    summary="End an interview session",
    description="Transitions session status from 'running' to 'completed'.",
    responses={
        409: {"description": "Invalid state transition"},
        404: {"description": "Session not found"},
    },
)
async def end_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
    _user: CurrentUser,
) -> SessionResponse:
    return await service.end_session(session_id)


@router.get(
    "/session/{session_id}",
    response_model=SessionResponse,
    summary="Get full session state",
    responses={
        404: {"description": "Session not found"},
    },
)
async def get_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
    _user: CurrentUser,
) -> SessionResponse:
    return await service.get_session(session_id)
