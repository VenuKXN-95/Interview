"""
JD service — parse files or raw text, extract structure via LLM, persist.
"""
import logging
from typing import Literal

from app.core.exceptions import EmptyDocumentException, JDNotFoundException
from app.llm.client import OpenRouterClient
from app.models.jd import ParsedJD
from app.parsers.docx_parser import DOCXParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.txt_parser import TXTParser
from app.prompts import jd_extraction as jd_prompt
from app.repositories.jd_repo import JDRepository
from app.schemas.jd import JDGetResponse, JDUploadResponse
from app.utils.file_utils import cleanup_temp_file, save_temp_file, validate_file_extension
from app.utils.validators import is_meaningful_text

logger = logging.getLogger(__name__)

_PARSERS = {
    "pdf": PDFParser(),
    "docx": DOCXParser(),
    "txt": TXTParser(),
}


class JDService:
    def __init__(self, repo: JDRepository, llm: OpenRouterClient) -> None:
        self._repo = repo
        self._llm = llm

    async def upload_and_parse(self, file_content: bytes, filename: str) -> JDUploadResponse:
        ext = validate_file_extension(filename)
        parser = _PARSERS[ext]

        tmp_path = await save_temp_file(file_content, ext)
        try:
            raw_text = parser.extract_text(tmp_path)
        finally:
            cleanup_temp_file(tmp_path)

        return await self._process_text(raw_text, source_type=ext)  # type: ignore[arg-type]

    async def parse_raw_text(self, raw_text: str) -> JDUploadResponse:
        if not is_meaningful_text(raw_text, min_chars=50):
            raise EmptyDocumentException(
                message="The job description text is too short to process.",
                details={"char_count": len(raw_text.strip())},
            )
        return await self._process_text(raw_text, source_type="raw_text")

    async def get_jd(self, jd_id: str) -> JDGetResponse:
        doc = await self._repo.get_by_id(jd_id)
        if not doc:
            raise JDNotFoundException(details={"jd_id": jd_id})
        return JDGetResponse(
            jd_id=doc["_id"],
            source_type=doc["source_type"],
            parsed_data=ParsedJD(**doc["parsed_data"]),
            created_at=doc["created_at"],
        )

    async def _process_text(
        self, raw_text: str, source_type: Literal["pdf", "docx", "txt", "raw_text"]
    ) -> JDUploadResponse:
        if not is_meaningful_text(raw_text, min_chars=50):
            raise EmptyDocumentException(
                message="The job description appears to be empty.",
                details={"char_count": len(raw_text.strip())},
            )

        parsed_data = await self._extract_structured(raw_text)

        doc = {
            "source_type": source_type,
            "raw_text": raw_text,
            "parsed_data": parsed_data.model_dump(),
        }
        jd_id = await self._repo.create(doc)
        logger.info("JD created", extra={"jd_id": jd_id, "source_type": source_type})

        return JDUploadResponse(jd_id=jd_id, source_type=source_type, parsed_data=parsed_data)

    async def _extract_structured(self, raw_text: str) -> ParsedJD:
        try:
            data = await self._llm.complete_json(
                user_prompt=jd_prompt.build_extraction_prompt(raw_text),
                system_prompt=jd_prompt.SYSTEM_PROMPT,
                temperature=0.1,
            )
            return ParsedJD(
                role=data.get("role", ""),
                company=data.get("company", ""),
                required_skills=data.get("required_skills", []),
                preferred_skills=data.get("preferred_skills", []),
                experience_required=data.get("experience_required", ""),
                responsibilities=data.get("responsibilities", []),
            )
        except Exception as exc:
            logger.warning("LLM JD extraction failed: %s — using empty parsed data", exc)
            return ParsedJD()
