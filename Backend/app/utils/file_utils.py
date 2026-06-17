"""
File handling utilities: MIME detection, temp file lifecycle,
size validation, and extension checking.
"""
import os
import tempfile
from pathlib import Path
from typing import AsyncIterator

import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import FileTooLargeException, UnsupportedFileTypeException

# Map of extension → canonical MIME types we accept
_EXTENSION_MIME_MAP: dict[str, list[str]] = {
    "pdf": ["application/pdf"],
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    ],
    "txt": ["text/plain"],
}


def get_extension(filename: str) -> str:
    """Return lowercase extension without the dot."""
    return Path(filename).suffix.lstrip(".").lower()


def validate_file_extension(filename: str) -> str:
    """Validate and return the file extension. Raises UnsupportedFileTypeException."""
    ext = get_extension(filename)
    if ext not in settings.allowed_extensions:
        raise UnsupportedFileTypeException(
            message=f"File type '.{ext}' is not allowed. Supported: {', '.join(settings.allowed_extensions)}",
            details={"received_extension": ext, "allowed": settings.allowed_extensions},
        )
    return ext


async def validate_file_size(file: UploadFile) -> bytes:
    """
    Read the entire file into memory, validate size, return bytes.
    Raises FileTooLargeException if exceeds limit.
    """
    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise FileTooLargeException(
            message=f"File size {len(content) / 1024 / 1024:.1f}MB exceeds limit of {settings.max_file_size_mb}MB.",
            details={
                "file_size_bytes": len(content),
                "max_bytes": settings.max_file_size_bytes,
            },
        )
    return content


async def save_temp_file(content: bytes, suffix: str) -> str:
    """
    Save bytes to a named temporary file. Returns the temp file path.
    Caller is responsible for cleanup (use cleanup_temp_file).
    """
    fd, tmp_path = tempfile.mkstemp(suffix=f".{suffix}")
    try:
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(content)
    finally:
        os.close(fd)
    return tmp_path


def cleanup_temp_file(path: str) -> None:
    """Silently remove a temp file."""
    try:
        os.unlink(path)
    except OSError:
        pass


def ensure_reports_dir() -> Path:
    """Create and return the reports directory."""
    path = Path(settings.reports_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path
