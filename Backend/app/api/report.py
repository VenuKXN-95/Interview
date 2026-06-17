"""
Report API routes.
GET /api/v1/report/{session_id}       — download PDF report
GET /api/v1/report/{session_id}/json  — get report as JSON
"""
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, JSONResponse

from app.api.deps import CurrentUser, get_report_service
from app.services.report_service import ReportService

router = APIRouter()


@router.get(
    "/report/{session_id}",
    summary="Generate and download PDF interview report",
    description=(
        "Generates a comprehensive PDF report including scores, recommendation, "
        "per-question evaluations, and coaching feedback. Cached after first generation."
    ),
    responses={
        200: {"content": {"application/pdf": {}}, "description": "PDF report file"},
        404: {"description": "Session or report not found"},
    },
)
async def download_report(
    session_id: str,
    service: Annotated[ReportService, Depends(get_report_service)],
    _user: CurrentUser,
) -> FileResponse:
    pdf_path = await service.get_or_generate_report(session_id)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"interview_report_{session_id}.pdf",
        headers={"Content-Disposition": f"attachment; filename=interview_report_{session_id}.pdf"},
    )


@router.get(
    "/report/{session_id}/json",
    summary="Get report data as JSON",
    description="Returns the full report data in JSON format without generating a PDF.",
    responses={404: {"description": "Report not found (generate PDF first)"}},
)
async def get_report_json(
    session_id: str,
    service: Annotated[ReportService, Depends(get_report_service)],
    _user: CurrentUser,
) -> JSONResponse:
    data = await service.get_report_json(session_id)
    # Remove internal MongoDB fields
    data.pop("_id", None)
    data.pop("pdf_path", None)
    return JSONResponse(content=data, media_type="application/json")
