"""
Pytest configuration and shared fixtures.
Uses mongomock-motor for in-memory MongoDB — no real DB needed.
"""
import asyncio
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


# ── Event loop ─────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ── Mock settings ──────────────────────────────────────────
@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Patch settings so tests don't need a .env file."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test_key")
    monkeypatch.setenv("MONGODB_URL", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DB_NAME", "test_db")


# ── Mock LLM client ────────────────────────────────────────
@pytest.fixture
def mock_llm():
    """Return a mock OpenRouterClient that returns predictable JSON."""
    llm = AsyncMock()
    llm.complete_json.return_value = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0100",
        "skills": ["Python", "FastAPI", "MongoDB"],
        "experience": [
            {"company": "TechCorp", "role": "Engineer", "duration": "2020-2024", "description": "Built APIs"}
        ],
        "projects": [
            {"name": "API Gateway", "description": "Rate limiting", "technologies": ["Python"]}
        ],
        "education": [
            {"institution": "University", "degree": "CS", "year": "2020"}
        ],
    }
    llm.complete.return_value = "Test LLM response"
    return llm


@pytest.fixture
def mock_eval_llm():
    """LLM mock that returns evaluation JSON."""
    llm = AsyncMock()
    llm.complete_json.return_value = {
        "score": 7,
        "category_scores": {
            "technical_accuracy": 7,
            "completeness": 6,
            "relevance": 8,
            "communication": 7,
        },
        "strengths": ["Good explanation", "Relevant example"],
        "weaknesses": ["Missing edge cases"],
        "missing_points": ["Error handling"],
        "summary": "Solid answer with room for improvement.",
    }
    return llm


# ── FastAPI test client ────────────────────────────────────
@pytest_asyncio.fixture
async def client(mock_settings):
    """Async HTTP test client for integration tests."""
    import os
    os.environ["OPENROUTER_API_KEY"] = "test_key"

    from main import app
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
