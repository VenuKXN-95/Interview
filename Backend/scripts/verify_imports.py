"""Quick import and sanity check for all application modules."""
import sys
sys.path.insert(0, ".")

print("Checking imports...")

from app.core.config import settings
from app.core.exceptions import AppException, ResumeNotFoundException, InvalidStateTransitionException
from app.core.logging import get_logger

from app.database.mongodb import get_database
from app.database.indexes import create_all_indexes

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.txt_parser import TXTParser

from app.llm.client import OpenRouterClient
from app.llm.response_parser import extract_json

from app.models.resume import ParsedResume, ResumeDocument
from app.models.jd import ParsedJD
from app.models.question import QuestionDocument
from app.models.session import InterviewSession, InterviewQuestion
from app.models.answer import AnswerDocument, EvaluationDocument
from app.models.report import ReportDocument

from app.repositories.base import BaseRepository
from app.repositories.resume_repo import ResumeRepository
from app.repositories.jd_repo import JDRepository
from app.repositories.question_repo import QuestionRepository
from app.repositories.session_repo import SessionRepository
from app.repositories.answer_repo import AnswerRepository
from app.repositories.evaluation_repo import EvaluationRepository
from app.repositories.report_repo import ReportRepository

from app.services.resume_service import ResumeService
from app.services.jd_service import JDService
from app.services.question_service import QuestionService
from app.services.interview_service import InterviewService
from app.services.session_service import SessionService, _VALID_TRANSITIONS
from app.services.answer_service import AnswerService
from app.services.evaluation_service import EvaluationService
from app.services.feedback_service import FeedbackService
from app.services.score_service import ScoreService, _get_recommendation, _weighted_avg
from app.services.report_service import ReportService

from app.prompts import resume_extraction, jd_extraction, question_generation
from app.prompts import answer_evaluation, feedback_generation

from app.reports.builder import build_report_pdf

from app.utils.file_utils import validate_file_extension
from app.utils.id_utils import new_object_id, validate_object_id
from app.utils.validators import clamp_score, extract_email

print("  All modules imported successfully!")
print()
print("Running sanity checks...")

# Settings
assert settings.app_name == "Mock Interview Backend"
assert settings.openrouter_model == "deepseek/deepseek-r1"
assert "pdf" in settings.allowed_extensions
print(f"  Settings: OK (model={settings.openrouter_model})")

# LLM response parser
assert extract_json('{"score": 7}') == {"score": 7}
assert extract_json("```json\n{\"x\": 1}\n```") == {"x": 1}
assert extract_json("no json here") is None
print("  extract_json: OK")

# Score utilities
assert clamp_score(15.0) == 10.0
assert clamp_score(-5.0) == 0.0
assert clamp_score(7.5) == 7.5
assert _weighted_avg([]) == 5.0
assert _weighted_avg([6.0, 8.0]) == 7.0
print("  Score utils: OK")

# Recommendations
assert _get_recommendation(9.5) == "strong_hire"
assert _get_recommendation(7.5) == "hire"
assert _get_recommendation(6.0) == "maybe"
assert _get_recommendation(4.0) == "no_hire"
print("  Recommendations: OK")

# Email extractor
assert extract_email("contact john@test.com for info") == "john@test.com"
assert extract_email("no email here") is None
print("  Email extractor: OK")

# ObjectId utils
oid = new_object_id()
assert len(oid) == 24
from app.core.exceptions import InvalidIDException
try:
    validate_object_id("not-an-id")
    assert False, "Should have raised"
except InvalidIDException:
    pass
print(f"  ObjectId utils: OK (sample={oid})")

# Session state machine transitions
assert "running" in _VALID_TRANSITIONS["created"]
assert "completed" in _VALID_TRANSITIONS["running"]
assert len(_VALID_TRANSITIONS["completed"]) == 0
print("  Session state machine: OK")

# Prompt builders
r_prompt = resume_extraction.build_extraction_prompt("John Doe, Software Engineer")
assert "JSON" in r_prompt
jd_prompt_text = jd_extraction.build_extraction_prompt("We are looking for a Python Engineer")
assert "JSON" in jd_prompt_text
print("  Prompt templates: OK")

# Pydantic models
pr = ParsedResume(name="John", email="j@j.com", skills=["Python"])
assert pr.name == "John"
assert "Python" in pr.skills
pjd = ParsedJD(role="Engineer", required_skills=["Python"])
assert pjd.role == "Engineer"
print("  Pydantic models: OK")

print()
print("=" * 50)
print("ALL CHECKS PASSED - Application is ready!")
print("=" * 50)
print()
print("Next steps:")
print("  1. cp .env.example .env  (and fill OPENROUTER_API_KEY)")
print("  2. python scripts/seed_questions.py")
print("  3. uvicorn main:app --reload --port 8000")
print("  4. Open http://localhost:8000/docs")
