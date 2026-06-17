"""
Structured logging setup for the application.
Outputs JSON in production, human-readable text in development.
Sensitive fields (api_key, password, token) are never logged.
"""
import logging
import sys
from typing import Any

from app.core.config import settings

# Fields that must never appear in logs
_SENSITIVE_KEYS = frozenset(
    {"api_key", "password", "token", "authorization", "secret", "openrouter_api_key"}
)


class _SensitiveFilter(logging.Filter):
    """Strip sensitive keys from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "extra"):
            record.extra = _redact(record.extra)  # type: ignore[attr-defined]
        return True


def _redact(data: Any) -> Any:
    if isinstance(data, dict):
        return {
            k: "***REDACTED***" if k.lower() in _SENSITIVE_KEYS else _redact(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_redact(item) for item in data]
    return data


def _build_json_formatter() -> logging.Formatter:
    try:
        import json

        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                log_obj: dict[str, Any] = {
                    "timestamp": self.formatTime(record, self.datefmt),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }
                if record.exc_info:
                    log_obj["exception"] = self.formatException(record.exc_info)
                extra = {
                    k: v
                    for k, v in record.__dict__.items()
                    if k
                    not in logging.LogRecord(
                        "", 0, "", 0, None, None, None
                    ).__dict__
                    and k not in ("message", "asctime")
                }
                if extra:
                    log_obj["extra"] = _redact(extra)
                return json.dumps(log_obj, default=str)

        return JsonFormatter()
    except Exception:
        return logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def setup_logging() -> None:
    """Configure application-wide logging. Call once at startup."""
    level = getattr(logging, settings.log_level, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(_SensitiveFilter())

    if settings.log_format == "json":
        handler.setFormatter(_build_json_formatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d — %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("motor", "pymongo", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger. Use module __name__ as the name."""
    return logging.getLogger(name)
