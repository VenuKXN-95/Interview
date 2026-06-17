"""
Unit tests for Session State Machine.
"""
import pytest
from unittest.mock import AsyncMock
from datetime import datetime, UTC

from app.services.session_service import SessionService
from app.core.exceptions import InvalidStateTransitionException, SessionNotFoundException


def _make_session(status: str) -> dict:
    return {
        "_id": "session_123",
        "resume_id": "res_1",
        "jd_id": "jd_1",
        "interview_type": "technical",
        "status": status,
        "question_count": 5,
        "questions": [],
        "started_at": None,
        "ended_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


class TestSessionStateMachine:
    @pytest.mark.asyncio
    async def test_start_from_created(self):
        repo = AsyncMock()
        repo.get_by_id.side_effect = [
            _make_session("created"),
            _make_session("running"),
        ]
        repo.update_status.return_value = None

        svc = SessionService(repo)
        result = await svc.start_session("session_123")
        assert result.status == "running"

    @pytest.mark.asyncio
    async def test_cannot_start_completed(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = _make_session("completed")

        svc = SessionService(repo)
        with pytest.raises(InvalidStateTransitionException):
            await svc.start_session("session_123")

    @pytest.mark.asyncio
    async def test_end_from_running(self):
        repo = AsyncMock()
        repo.get_by_id.side_effect = [
            _make_session("running"),
            _make_session("completed"),
        ]
        repo.update_status.return_value = None

        svc = SessionService(repo)
        result = await svc.end_session("session_123")
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_cannot_end_created(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = _make_session("created")

        svc = SessionService(repo)
        with pytest.raises(InvalidStateTransitionException):
            await svc.end_session("session_123")

    @pytest.mark.asyncio
    async def test_not_found_raises(self):
        repo = AsyncMock()
        repo.get_by_id.return_value = None

        svc = SessionService(repo)
        with pytest.raises(SessionNotFoundException):
            await svc.get_session("nonexistent")
