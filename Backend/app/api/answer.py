"""
Answer submission route.
POST /api/v1/answer/submit         — submit an answer (triggers LLM evaluation)
GET  /api/v1/answer/session/{id}   — get all answers for a session
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, get_answer_service
from app.schemas.answer import AnswerListResponse, SubmitAnswerRequest, SubmitAnswerResponse
from app.services.answer_service import AnswerService

router = APIRouter()


@router.post(
    "/answer/submit",
    response_model=SubmitAnswerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer and receive LLM evaluation",
    description=(
        "Submit a candidate answer for a specific question in a running session. "
        "The server immediately evaluates the answer using an LLM and returns "
        "score, strengths, weaknesses, and coaching feedback."
    ),
    responses={
        404: {"description": "Session not found"},
        409: {"description": "Session not running or duplicate answer"},
    },
)
async def submit_answer(
    body: SubmitAnswerRequest,
    service: Annotated[AnswerService, Depends(get_answer_service)],
    _user: CurrentUser,
) -> SubmitAnswerResponse:
    return await service.submit_answer(body)


@router.get(
    "/answer/session/{session_id}",
    summary="Get all submitted answers for a session",
    responses={400: {"description": "Invalid session ID"}},
)
async def get_session_answers(
    session_id: str,
    service: Annotated[AnswerService, Depends(get_answer_service)],
    _user: CurrentUser,
) -> dict:
    answers = await service.get_session_answers(session_id)
    return {"session_id": session_id, "answers": answers, "total": len(answers)}
