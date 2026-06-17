"""
Unit tests for Question Service — 100% AI generation.
"""
import pytest
from unittest.mock import AsyncMock

from app.services.question_service import QuestionService, _generic_fallback_questions

SAMPLE_RESUME = {
    "name": "Jane Smith",
    "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
    "experience": [
        {"company": "TechCorp", "role": "Backend Engineer", "duration": "2021-2024",
         "description": "Built microservices with FastAPI"}
    ],
    "projects": [
        {"name": "API Gateway", "description": "Rate limiting gateway", "technologies": ["Python", "Redis"]}
    ],
    "education": [{"degree": "B.Sc Computer Science", "institution": "MIT", "year": "2021"}],
}

SAMPLE_JD = {
    "role": "Senior Backend Engineer",
    "company": "Startup Inc",
    "required_skills": ["Python", "MongoDB", "REST APIs"],
    "preferred_skills": ["FastAPI", "Docker"],
    "responsibilities": ["Build scalable APIs", "Optimize DB queries"],
    "experience_required": "3+ years",
}

AI_RESPONSE_10 = {
    "questions": [
        {
            "question": f"In your API Gateway project, how did you implement rate limiting?",
            "category": "Technical",
            "difficulty": "medium",
            "rationale": "Tests hands-on knowledge of their specific project",
        }
        for _ in range(10)
    ]
}

AI_RESPONSE_5 = {
    "questions": [
        {
            "question": f"Question {i}",
            "category": "Technical",
            "difficulty": "medium",
            "rationale": "Test",
        }
        for i in range(5)
    ]
}


class TestQuestionService:
    """All questions generated 100% by AI."""

    @pytest.mark.asyncio
    async def test_all_questions_ai_generated(self):
        """Primary flow: LLM generates all questions, no bank needed."""
        mock_repo = AsyncMock()
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = AI_RESPONSE_10

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "technical", total_count=10
        )

        assert len(questions) == 10
        assert all(q["source"] == "ai_generated" for q in questions)
        # Bank should NOT be called in the primary path
        mock_repo.get_random_sample.assert_not_called()
        mock_repo.get_count_by_type.assert_not_called()

    @pytest.mark.asyncio
    async def test_questions_have_sequential_order(self):
        """All questions must have order 1..N."""
        mock_repo = AsyncMock()
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = AI_RESPONSE_10

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "hr", total_count=10
        )

        orders = sorted(q["order"] for q in questions)
        assert orders == list(range(1, 11))

    @pytest.mark.asyncio
    async def test_questions_have_unique_ids(self):
        """Each question must have a unique question_id."""
        mock_repo = AsyncMock()
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = AI_RESPONSE_10

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "technical", total_count=10
        )

        ids = [q["question_id"] for q in questions]
        assert len(set(ids)) == 10  # All unique

    @pytest.mark.asyncio
    async def test_topup_from_bank_when_llm_returns_partial(self):
        """
        If LLM returns fewer questions than requested (e.g. 5 of 10),
        the service tops up from the bank automatically.
        """
        mock_repo = AsyncMock()
        mock_repo.get_count_by_type.return_value = 100  # Bank has questions
        mock_repo.get_random_sample.return_value = [
            {"_id": f"bank_{i}", "question": f"Bank Q{i}", "category": "Technical",
             "difficulty": "medium", "tags": [], "interview_type": "technical"}
            for i in range(5)
        ]
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = AI_RESPONSE_5  # Only 5 returned

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "technical", total_count=10
        )

        assert len(questions) == 10
        ai_count = sum(1 for q in questions if q["source"] == "ai_generated")
        bank_count = sum(1 for q in questions if q["source"] == "bank")
        assert ai_count == 5
        assert bank_count == 5

    @pytest.mark.asyncio
    async def test_fallback_to_bank_when_llm_fails(self):
        """
        If LLM completely fails, fall back to question bank.
        No exception should propagate to the caller.
        """
        async def bank_side_effect(interview_type, count, difficulty_mix=None):
            return [
                {"_id": f"bank_{i}", "question": f"Bank Q{i}", "category": "Technical",
                 "difficulty": "medium", "tags": []}
                for i in range(count)
            ]

        mock_repo = AsyncMock()
        mock_repo.get_count_by_type.return_value = 100
        mock_repo.get_random_sample.side_effect = bank_side_effect

        mock_llm = AsyncMock()
        mock_llm.complete_json.side_effect = Exception("LLM API timeout")

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "technical", total_count=10
        )

        assert len(questions) == 10
        assert all(q["source"] == "bank" for q in questions)

    @pytest.mark.asyncio
    async def test_generic_fallback_when_both_llm_and_bank_fail(self):
        """
        Last resort: if LLM fails AND bank is empty, return hardcoded generic questions.
        The interview must still proceed.
        """
        mock_repo = AsyncMock()
        mock_repo.get_count_by_type.return_value = 0  # Empty bank
        mock_repo.get_random_sample.return_value = []

        mock_llm = AsyncMock()
        mock_llm.complete_json.side_effect = Exception("LLM down")

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "hr", total_count=10
        )

        assert len(questions) == 10
        assert all(q["source"] == "generic" for q in questions)

    @pytest.mark.asyncio
    async def test_different_interview_types(self):
        """AI generation must work for all 4 interview types."""
        mock_repo = AsyncMock()
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = AI_RESPONSE_10

        svc = QuestionService(mock_repo, mock_llm)

        for itype in ["hr", "technical", "telephonic", "virtual"]:
            questions = await svc.generate_interview_questions(
                SAMPLE_RESUME, SAMPLE_JD, itype, total_count=5
            )
            assert len(questions) == 5, f"Failed for type: {itype}"
            assert all(q["source"] == "ai_generated" for q in questions)

    @pytest.mark.asyncio
    async def test_empty_question_text_filtered(self):
        """LLM responses with empty question text are filtered out."""
        mock_repo = AsyncMock()
        mock_repo.get_count_by_type.return_value = 100
        mock_repo.get_random_sample.return_value = [
            {"_id": f"b{i}", "question": f"BQ{i}", "category": "T", "difficulty": "medium", "tags": []}
            for i in range(10)
        ]
        mock_llm = AsyncMock()
        mock_llm.complete_json.return_value = {
            "questions": [
                {"question": "Valid question?", "category": "Technical", "difficulty": "medium", "rationale": "ok"},
                {"question": "", "category": "Technical", "difficulty": "easy", "rationale": "empty"},
                {"question": "   ", "category": "Technical", "difficulty": "easy", "rationale": "blank"},
            ]
        }

        svc = QuestionService(mock_repo, mock_llm)
        questions = await svc.generate_interview_questions(
            SAMPLE_RESUME, SAMPLE_JD, "technical", total_count=5
        )
        # Only 1 valid AI question, 4 topped up from bank
        assert len(questions) == 5
        valid_ai = [q for q in questions if q["source"] == "ai_generated" and q["question_text"]]
        assert len(valid_ai) == 1


class TestGenericFallback:
    """Unit tests for the hardcoded generic fallback."""

    def test_returns_correct_count(self):
        questions = _generic_fallback_questions("hr", 10)
        assert len(questions) == 10

    def test_returns_correct_count_exceeding_pool(self):
        """When count > pool size, cycles through the pool."""
        questions = _generic_fallback_questions("technical", 15)
        assert len(questions) == 15

    def test_source_is_generic(self):
        questions = _generic_fallback_questions("technical", 5)
        assert all(q["source"] == "generic" for q in questions)

    def test_all_interview_types_have_questions(self):
        for itype in ["hr", "technical", "telephonic", "virtual"]:
            questions = _generic_fallback_questions(itype, 5)
            assert len(questions) == 5
            assert all(q["question_text"] for q in questions)
