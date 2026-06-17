"""
Pydantic V2 schemas for the JD API.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.jd import ParsedJD


class JDUploadResponse(BaseModel):
    jd_id: str
    source_type: str
    parsed_data: ParsedJD

    model_config = {
        "json_schema_extra": {
            "example": {
                "jd_id": "665f1a2b3c4d5e6f7a8b9c0e",
                "source_type": "pdf",
                "parsed_data": {
                    "role": "Senior Backend Engineer",
                    "company": "TechCorp",
                    "required_skills": ["Python", "FastAPI", "MongoDB", "Docker"],
                    "preferred_skills": ["Kubernetes", "Redis", "GraphQL"],
                    "experience_required": "4+ years",
                    "responsibilities": [
                        "Design and implement RESTful APIs",
                        "Optimize database performance",
                        "Mentor junior engineers",
                    ],
                },
            }
        }
    }


class JDRawTextRequest(BaseModel):
    """Request body for submitting raw JD text directly."""

    text: str = Field(
        ...,
        min_length=50,
        description="Raw job description text",
        examples=["We are looking for a Senior Backend Engineer with 5+ years..."],
    )


class JDGetResponse(JDUploadResponse):
    created_at: datetime
