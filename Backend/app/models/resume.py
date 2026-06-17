"""
Domain model for Resume.
These are pure Python dataclasses / Pydantic models — no DB coupling.
"""
from datetime import datetime, UTC
from typing import Any

from pydantic import BaseModel, Field


class ExperienceEntry(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    description: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    year: str = ""


class ParsedResume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)


class ResumeDocument(BaseModel):
    """Represents a resume document as stored in MongoDB."""

    id: str = Field(alias="_id", default="")
    filename: str
    file_type: str
    raw_text: str
    parsed_data: ParsedResume
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
