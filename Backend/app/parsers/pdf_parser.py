"""
PDF text extractor.
Primary: pdfplumber (better table/layout handling)
Fallback: pymupdf (fitz) — faster, better for scanned/image PDFs
"""
import logging

from app.core.exceptions import ParseFailureException
from app.parsers.base import BaseParser

logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        """Try pdfplumber first, fall back to pymupdf on failure."""
        text = self._try_pdfplumber(file_path)
        if not text or len(text.strip()) < 20:
            logger.info("pdfplumber returned sparse text, trying pymupdf fallback.")
            text = self._try_pymupdf(file_path)
        if not text:
            raise ParseFailureException(
                message="Could not extract text from the PDF. It may be image-only or corrupted.",
                details={"file_path": file_path},
            )
        return text.strip()

    def _try_pdfplumber(self, file_path: str) -> str:
        try:
            import pdfplumber

            pages: list[str] = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
            return "\n".join(pages)
        except Exception as exc:
            logger.warning("pdfplumber failed: %s", exc)
            return ""

    def _try_pymupdf(self, file_path: str) -> str:
        try:
            import fitz  # pymupdf

            doc = fitz.open(file_path)
            pages: list[str] = []
            for page in doc:
                pages.append(page.get_text())
            doc.close()
            return "\n".join(pages)
        except Exception as exc:
            logger.warning("pymupdf failed: %s", exc)
            return ""
