"""
Pydantic V2 request/response schemas for the Resume API.
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.resume import ParsedResume


class ResumeUploadResponse(BaseModel):
    """Response for POST /resume/upload"""

    resume_id: str = Field(..., description="MongoDB ObjectId of the created resume")
    filename: str
    file_type: str
    parsed_data: ParsedResume

    model_config = {
        "json_schema_extra": {
            "example": {
                "resume_id": "665f1a2b3c4d5e6f7a8b9c0d",
                "filename": "john_doe_resume.pdf",
                "file_type": "pdf",
                "parsed_data": {
                    "name": "John Doe",
                    "email": "john.doe@email.com",
                    "phone": "+1-555-0100",
                    "skills": ["Python", "FastAPI", "MongoDB", "Docker"],
                    "experience": [
                        {
                            "company": "TechCorp",
                            "role": "Senior Backend Engineer",
                            "duration": "2021-2024",
                            "description": "Built microservices for payment platform.",
                        }
                    ],
                    "projects": [
                        {
                            "name": "API Gateway",
                            "description": "High-throughput API gateway with rate limiting.",
                            "technologies": ["Python", "Redis", "nginx"],
                        }
                    ],
                    "education": [
                        {
                            "institution": "State University",
                            "degree": "B.Tech Computer Science",
                            "year": "2020",
                        }
                    ],
                },
            }
        }
    }


class ResumeGetResponse(ResumeUploadResponse):
    """Response for GET /resume/{resume_id}"""

    created_at: datetime
