import logging

from fastapi import FastAPI
from sqlalchemy import text

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine

setup_logging()
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    def startup_event() -> None:
        logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)

        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection check passed.")
        except Exception:
            logger.exception("Database connection check failed.")
            raise

    return app


app = create_app()