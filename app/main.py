import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import RequestLoggingMiddleware, setup_logging
from app.db import session as session_module
from app.tools.job_fetcher import JobFetchError
from app.tools.resume_extractor import ResumeExtractionError

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

    try:
        with session_module.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("Database connection check passed.")
    except Exception:
        logger.exception("Database connection check failed.")
        raise

    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.exception_handler(ResumeExtractionError)
    async def resume_extraction_exception_handler(
        request: Request,
        exc: ResumeExtractionError,
    ) -> JSONResponse:
        logging.getLogger("app.errors").warning(
            "resume_extraction_error request_id=%s path=%s detail=%s",
            getattr(request.state, "request_id", "unknown"),
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(JobFetchError)
    async def job_fetch_exception_handler(
        request: Request,
        exc: JobFetchError,
    ) -> JSONResponse:
        logging.getLogger("app.errors").warning(
            "job_fetch_error request_id=%s path=%s detail=%s",
            getattr(request.state, "request_id", "unknown"),
            request.url.path,
            str(exc),
        )
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logging.getLogger("app.errors").exception(
            "unhandled_exception request_id=%s path=%s",
            getattr(request.state, "request_id", "unknown"),
            request.url.path,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    return app


app = create_app()