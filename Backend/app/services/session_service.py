"""
Session state machine service.
Valid transitions: created → running → completed
"""
import logging
from datetime import datetime, UTC

from app.core.exceptions import InvalidStateTransitionException, SessionNotFoundException
from app.models.session import InterviewQuestion
from app.repositories.session_repo import SessionRepository
from app.schemas.session import SessionResponse

logger = logging.getLogger(__name__)

# Allowed state transitions
_VALID_TRANSITIONS = {
    "created": {"running"},
    "running": {"completed", "abandoned"},
    "completed": set(),
    "abandoned": set(),
}


class SessionService:
    def __init__(self, repo: SessionRepository) -> None:
        self._repo = repo

    async def get_session(self, session_id: str) -> SessionResponse:
        doc = await self._repo.get_by_id(session_id)
        if not doc:
            raise SessionNotFoundException(details={"session_id": session_id})
        return _doc_to_response(doc)

    async def start_session(self, session_id: str) -> SessionResponse:
        doc = await self._repo.get_by_id(session_id)
        if not doc:
            raise SessionNotFoundException(details={"session_id": session_id})

        self._assert_transition(doc["status"], "running", session_id)

        await self._repo.update_status(
            session_id, "running", extra_fields={"started_at": datetime.now(UTC)}
        )
        logger.info("Session started", extra={"session_id": session_id})
        return await self.get_session(session_id)

    async def end_session(self, session_id: str) -> SessionResponse:
        doc = await self._repo.get_by_id(session_id)
        if not doc:
            raise SessionNotFoundException(details={"session_id": session_id})

        self._assert_transition(doc["status"], "completed", session_id)

        await self._repo.update_status(
            session_id, "completed", extra_fields={"ended_at": datetime.now(UTC)}
        )
        logger.info("Session completed", extra={"session_id": session_id})
        return await self.get_session(session_id)

    def _assert_transition(
        self, current: str, target: str, session_id: str
    ) -> None:
        if target not in _VALID_TRANSITIONS.get(current, set()):
            raise InvalidStateTransitionException(
                message=f"Cannot move session from '{current}' to '{target}'.",
                details={
                    "session_id": session_id,
                    "current_status": current,
                    "attempted_status": target,
                },
            )


def _doc_to_response(doc: dict) -> SessionResponse:
    return SessionResponse(
        session_id=doc["_id"],
        resume_id=doc["resume_id"],
        jd_id=doc["jd_id"],
        interview_type=doc["interview_type"],
        status=doc["status"],
        question_count=doc.get("question_count", 0),
        questions=[InterviewQuestion(**q) for q in doc.get("questions", [])],
        started_at=doc.get("started_at"),
        ended_at=doc.get("ended_at"),
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )
