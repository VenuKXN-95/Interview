"""
Session route file (mirrors interview.py for standalone session routes).
"""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_session_service
from app.schemas.session import SessionResponse
from app.services.session_service import SessionService

router = APIRouter()


@router.get(
    "/session/{session_id}",
    response_model=SessionResponse,
    summary="Get full session state",
    tags=["Session"],
)
async def get_session(
    session_id: str,
    service: Annotated[SessionService, Depends(get_session_service)],
) -> SessionResponse:
    return await service.get_session(session_id)
