from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup logic
    # e.g. load settings, warm caches, initialize services
    yield
    # shutdown logic
    # e.g. cleanup resources


app = FastAPI(
    title="Resume Lens API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(api_router, prefix="/api/v1")