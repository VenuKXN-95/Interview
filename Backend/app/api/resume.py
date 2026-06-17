"""
Resume API routes — JWT protected.
POST /api/v1/resume/upload  — upload & parse a resume file
GET  /api/v1/resume/{id}   — retrieve a parsed resume
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import CurrentUser, get_resume_service
from app.schemas.resume import ResumeGetResponse, ResumeUploadResponse
from app.services.resume_service import ResumeService
from app.utils.file_utils import validate_file_size

router = APIRouter()


@router.post(
    "/resume/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a resume",
    responses={
        401: {"description": "Not authenticated"},
        413: {"description": "File exceeds size limit"},
        415: {"description": "Unsupported file type"},
        422: {"description": "Empty or unreadable document"},
    },
)
async def upload_resume(
    file: Annotated[UploadFile, File(description="Resume file (PDF, DOCX, TXT)")],
    service: Annotated[ResumeService, Depends(get_resume_service)],
    _user: CurrentUser,
) -> ResumeUploadResponse:
    content = await validate_file_size(file)
    return await service.upload_and_parse(content, file.filename or "resume")


@router.get(
    "/resume/{resume_id}",
    response_model=ResumeGetResponse,
    summary="Get a parsed resume by ID",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Resume not found"},
    },
)
async def get_resume(
    resume_id: str,
    service: Annotated[ResumeService, Depends(get_resume_service)],
    _user: CurrentUser,
) -> ResumeGetResponse:
    return await service.get_resume(resume_id)
