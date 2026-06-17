"""
Custom exception hierarchy for the application.
All domain-specific errors inherit from AppException.
FastAPI exception handlers are registered in main.py.
"""
from typing import Any


class AppException(Exception):
    """Base class for all application exceptions."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        error_code: str | None = None,
        details: Any = None,
        status_code: int | None = None,
    ) -> None:
        self.message = message or self.__class__.message
        self.error_code = error_code or self.__class__.error_code
        self.details = details
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details is not None:
            payload["details"] = self.details
        return payload


# ── 400 Bad Request ──────────────────────────────────────────
class BadRequestException(AppException):
    status_code = 400
    error_code = "BAD_REQUEST"
    message = "Invalid request."


class InvalidIDException(AppException):
    status_code = 400
    error_code = "INVALID_ID"
    message = "The provided ID is not a valid ObjectId."


# ── 404 Not Found ────────────────────────────────────────────
class NotFoundException(AppException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "The requested resource was not found."


class ResumeNotFoundException(NotFoundException):
    error_code = "RESUME_NOT_FOUND"
    message = "Resume not found."


class JDNotFoundException(NotFoundException):
    error_code = "JD_NOT_FOUND"
    message = "Job description not found."


class SessionNotFoundException(NotFoundException):
    error_code = "SESSION_NOT_FOUND"
    message = "Interview session not found."


class AnswerNotFoundException(NotFoundException):
    error_code = "ANSWER_NOT_FOUND"
    message = "Answer not found."


class ReportNotFoundException(NotFoundException):
    error_code = "REPORT_NOT_FOUND"
    message = "Report not found."


# ── 409 Conflict ─────────────────────────────────────────────
class ConflictException(AppException):
    status_code = 409
    error_code = "CONFLICT"
    message = "A conflict occurred."


class InvalidStateTransitionException(ConflictException):
    error_code = "INVALID_STATE_TRANSITION"
    message = "Cannot perform this action in the current session state."


class SessionNotRunningException(ConflictException):
    error_code = "SESSION_NOT_RUNNING"
    message = "The session is not currently running."


class DuplicateAnswerException(ConflictException):
    error_code = "DUPLICATE_ANSWER"
    message = "An answer has already been submitted for this question."


# ── 413 Request Entity Too Large ─────────────────────────────
class FileTooLargeException(AppException):
    status_code = 413
    error_code = "FILE_TOO_LARGE"
    message = "The uploaded file exceeds the maximum allowed size."


# ── 415 Unsupported Media Type ───────────────────────────────
class UnsupportedFileTypeException(AppException):
    status_code = 415
    error_code = "UNSUPPORTED_FORMAT"
    message = "The uploaded file type is not supported."


# ── 422 Unprocessable Entity ─────────────────────────────────
class EmptyDocumentException(AppException):
    status_code = 422
    error_code = "EMPTY_DOCUMENT"
    message = "The document appears to be empty or could not be parsed."


class ParseFailureException(AppException):
    status_code = 422
    error_code = "PARSE_FAILURE"
    message = "Failed to parse the uploaded document."


# ── 503 Service Unavailable ───────────────────────────────────
class LLMServiceException(AppException):
    status_code = 503
    error_code = "LLM_SERVICE_ERROR"
    message = "The AI service is currently unavailable. Please try again."


class LLMResponseParseException(AppException):
    status_code = 503
    error_code = "LLM_RESPONSE_PARSE_ERROR"
    message = "Failed to parse the AI service response."
