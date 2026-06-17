"""
Domain model for Job Description.
"""
from datetime import datetime, UTC
from typing import Literal

from pydantic import BaseModel, Field


class ParsedJD(BaseModel):
    role: str = ""
    company: str = ""
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_required: str = ""
    responsibilities: list[str] = Field(default_factory=list)


class JDDocument(BaseModel):
    id: str = Field(alias="_id", default="")
    source_type: Literal["pdf", "docx", "txt", "raw_text"]
    raw_text: str
    parsed_data: ParsedJD
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
