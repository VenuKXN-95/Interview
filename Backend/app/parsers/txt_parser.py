"""
Plain text parser — reads file with UTF-8 (fallback to latin-1).
"""
import logging

from app.core.exceptions import ParseFailureException
from app.parsers.base import BaseParser

logger = logging.getLogger(__name__)


class TXTParser(BaseParser):
    def extract_text(self, file_path: str) -> str:
        for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                with open(file_path, encoding=encoding) as f:
                    text = f.read()
                if text.strip():
                    return text.strip()
            except UnicodeDecodeError:
                continue
            except Exception as exc:
                logger.exception("TXT parse failed: %s", exc)
                raise ParseFailureException(
                    message=f"Failed to read TXT file: {exc}",
                    details={"file_path": file_path},
                )
        raise ParseFailureException(
            message="The TXT file could not be decoded with any supported encoding.",
            details={"file_path": file_path},
        )
