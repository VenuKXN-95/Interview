"""
FastAPI application entrypoint.
Registers lifespan, middleware, routers, and exception handlers.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging
from app.database.indexes import create_all_indexes
from app.database.mongodb import close_db, connect_db, get_database
from app.utils.file_utils import ensure_reports_dir

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup → yield → shutdown."""
    # Startup
    logger.info(
        "Starting %s v%s [%s]",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    await connect_db()
    db = get_database()
    await create_all_indexes(db)
    ensure_reports_dir()
    logger.info("Application startup complete.")

    yield

    # Shutdown
    await close_db()
    logger.info("Application shutdown complete.")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-Powered Mock Interview Platform Backend. "
            "Supports HR, Technical, Telephonic, and Virtual interview types."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        debug=settings.debug,
    )

    # ── CORS ────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception Handlers ──────────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning(
            "Application exception: %s",
            exc.error_code,
            extra={"path": request.url.path, "error": exc.to_dict()},
        )
        response = JSONResponse(status_code=exc.status_code, content=exc.to_dict())
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "Unhandled exception on %s: %s", request.url.path, str(exc)
        )
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "INTERNAL_ERROR", "message": "An unexpected error occurred."},
        )
        origin = request.headers.get("origin")
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "*"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

    # ── Routers ─────────────────────────────────────────────
    from app.api import answer, auth, interview, jd, report, resume, session

    API_PREFIX = "/api/v1"
    app.include_router(auth.router, prefix=API_PREFIX)
    app.include_router(resume.router, prefix=API_PREFIX, tags=["Resume"])
    app.include_router(jd.router, prefix=API_PREFIX, tags=["Job Description"])
    app.include_router(interview.router, prefix=API_PREFIX, tags=["Interview"])
    app.include_router(session.router, prefix=API_PREFIX, tags=["Session"])
    app.include_router(answer.router, prefix=API_PREFIX, tags=["Answer"])
    app.include_router(report.router, prefix=API_PREFIX, tags=["Report"])

    # ── Health check ────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health Check")
    async def health() -> dict:
        return {"status": "ok", "version": settings.app_version}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_config=None,  # Use our own logging setup
    )
