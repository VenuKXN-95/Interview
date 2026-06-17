"""
Job Description API routes.
POST /api/v1/jd/upload   — upload JD file
POST /api/v1/jd/raw      — submit raw text JD
GET  /api/v1/jd/{id}     — retrieve parsed JD
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.deps import CurrentUser, get_jd_service
from app.schemas.jd import JDGetResponse, JDRawTextRequest, JDUploadResponse
from app.services.jd_service import JDService
from app.utils.file_utils import validate_file_size

router = APIRouter()


@router.post(
    "/jd/upload",
    response_model=JDUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a Job Description file",
    responses={
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
        422: {"description": "Empty document"},
    },
)
async def upload_jd(
    file: Annotated[UploadFile, File(description="JD file (PDF, DOCX, TXT)")],
    service: Annotated[JDService, Depends(get_jd_service)],
    _user: CurrentUser,
) -> JDUploadResponse:
    content = await validate_file_size(file)
    return await service.upload_and_parse(content, file.filename or "jd")


@router.post(
    "/jd/raw",
    response_model=JDUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit raw job description text",
    description="Accepts plain text of the job description instead of a file.",
)
async def submit_raw_jd(
    body: JDRawTextRequest,
    service: Annotated[JDService, Depends(get_jd_service)],
    _user: CurrentUser,
) -> JDUploadResponse:
    return await service.parse_raw_text(body.text)


@router.get(
    "/jd/{jd_id}",
    response_model=JDGetResponse,
    summary="Get a parsed JD by ID",
    responses={
        400: {"description": "Invalid ObjectId"},
        404: {"description": "JD not found"},
    },
)
async def get_jd(
    jd_id: str,
    service: Annotated[JDService, Depends(get_jd_service)],
    _user: CurrentUser,
) -> JDGetResponse:
    return await service.get_jd(jd_id)
