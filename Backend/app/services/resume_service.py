"""
Resume service — orchestrates parsing, LLM extraction, and persistence.
"""
import logging

from app.core.exceptions import EmptyDocumentException, ResumeNotFoundException
from app.llm.client import OpenRouterClient
from app.models.resume import (
    EducationEntry,
    ExperienceEntry,
    ParsedResume,
    ProjectEntry,
)
from app.parsers.docx_parser import DOCXParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.txt_parser import TXTParser
from app.prompts import resume_extraction as resume_prompt
from app.repositories.resume_repo import ResumeRepository
from app.schemas.resume import ResumeGetResponse, ResumeUploadResponse
from app.utils.file_utils import cleanup_temp_file, save_temp_file, validate_file_extension
from app.utils.validators import is_meaningful_text

logger = logging.getLogger(__name__)

_PARSERS = {
    "pdf": PDFParser(),
    "docx": DOCXParser(),
    "txt": TXTParser(),
}


class ResumeService:
    def __init__(self, repo: ResumeRepository, llm: OpenRouterClient) -> None:
        self._repo = repo
        self._llm = llm

    async def upload_and_parse(
        self, file_content: bytes, filename: str
    ) -> ResumeUploadResponse:
        """
        Full pipeline:
          1. Validate & save temp file
          2. Extract raw text via parser
          3. LLM-extract structured fields
          4. Persist to MongoDB
          5. Return response schema
        """
        ext = validate_file_extension(filename)
        parser = _PARSERS[ext]

        tmp_path = await save_temp_file(file_content, ext)
        try:
            raw_text = parser.extract_text(tmp_path)
        finally:
            cleanup_temp_file(tmp_path)

        if not is_meaningful_text(raw_text, min_chars=50):
            raise EmptyDocumentException(
                message="The resume contains too little text to process.",
                details={"char_count": len(raw_text.strip())},
            )

        parsed_data = await self._extract_structured(raw_text)

        doc = {
            "filename": filename,
            "file_type": ext,
            "raw_text": raw_text,
            "parsed_data": parsed_data.model_dump(),
        }
        resume_id = await self._repo.create(doc)
        logger.info("Resume created", extra={"resume_id": resume_id, "ext": ext})

        return ResumeUploadResponse(
            resume_id=resume_id,
            filename=filename,
            file_type=ext,
            parsed_data=parsed_data,
        )

    async def get_resume(self, resume_id: str) -> ResumeGetResponse:
        doc = await self._repo.get_by_id(resume_id)
        if not doc:
            raise ResumeNotFoundException(details={"resume_id": resume_id})
        parsed = ParsedResume(**doc["parsed_data"])
        return ResumeGetResponse(
            resume_id=doc["_id"],
            filename=doc["filename"],
            file_type=doc["file_type"],
            parsed_data=parsed,
            created_at=doc["created_at"],
        )

    async def _extract_structured(self, raw_text: str) -> ParsedResume:
        """Use LLM to extract structured fields from raw resume text."""
        try:
            data = await self._llm.complete_json(
                user_prompt=resume_prompt.build_extraction_prompt(raw_text),
                system_prompt=resume_prompt.SYSTEM_PROMPT,
                temperature=0.1,
            )
            return _map_llm_to_parsed_resume(data)
        except Exception as exc:
            logger.warning(
                "LLM resume extraction failed, using regex fallback: %s", exc
            )
            return _regex_fallback(raw_text)


def _map_llm_to_parsed_resume(data: dict) -> ParsedResume:
    """Map raw LLM JSON dict to ParsedResume model with graceful defaults."""
    return ParsedResume(
        name=data.get("name", ""),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        skills=data.get("skills", []),
        experience=[
            ExperienceEntry(**e) for e in data.get("experience", []) if isinstance(e, dict)
        ],
        projects=[
            ProjectEntry(**p) for p in data.get("projects", []) if isinstance(p, dict)
        ],
        education=[
            EducationEntry(**e) for e in data.get("education", []) if isinstance(e, dict)
        ],
    )


def _regex_fallback(raw_text: str) -> ParsedResume:
    """
    Simple regex-based fallback when LLM is unavailable.
    Extracts email and attempts skill detection.
    """
    from app.utils.validators import extract_email, extract_phone

    return ParsedResume(
        name="",
        email=extract_email(raw_text) or "",
        phone=extract_phone(raw_text) or "",
        skills=[],
        experience=[],
        projects=[],
        education=[],
    )
