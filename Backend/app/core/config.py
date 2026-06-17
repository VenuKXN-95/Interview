"""
Core application configuration using pydantic-settings.
All settings are loaded from environment variables / .env file.
"""
from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────
    app_name: str = "Mock Interview Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: Literal["development", "staging", "production"] = "development"

    # ── Server ───────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── MongoDB ──────────────────────────────────────────────
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "mock_interview_db"

    # ── OpenRouter ───────────────────────────────────────────
    openrouter_api_key: str = Field(default="", description="OpenRouter API key — required for LLM features")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "deepseek/deepseek-r1"
    openrouter_fallback_model: str = "qwen/qwen3-32b"
    openrouter_timeout: int = 90
    openrouter_max_retries: int = 3

    # ── File Upload ───────────────────────────────────────────
    max_file_size_mb: int = 10
    # Declared as Any so pydantic-settings doesn't JSON-parse before our validator
    allowed_extensions: Any = ["pdf", "docx", "txt"]

    # ── Report Storage ────────────────────────────────────────
    reports_dir: str = "./generated_reports"

    # ── Logging ───────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["json", "text"] = "json"

    # ── CORS ──────────────────────────────────────────────────
    # Declared as Any so pydantic-settings doesn't JSON-parse before our validator
    cors_origins: Any = ["http://localhost:3000", "http://localhost:5173"]

    # ── JWT Authentication ────────────────────────────────────
    jwt_secret_key: str = Field(default="change-me-in-production", description="JWT signing secret")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Derived properties ────────────────────────────────────
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",")]
        return [ext.lower() for ext in v]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list) -> list[str]:
        if isinstance(v, str):
            import json

            try:
                return json.loads(v)
            except Exception:
                return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — called via FastAPI Depends()."""
    return Settings()


# Module-level alias for convenience imports
settings = get_settings()
