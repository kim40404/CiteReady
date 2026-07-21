"""CiteReady — AI Search Visibility Scoring Engine.

Main FastAPI application entry point.
Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api_router import api_router
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import get_logger, setup_logging

# Initialize structured logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────────
    logger.info(
        "app.startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    await init_db()
    logger.info("app.database_ready")

    yield  # App is running

    # ── Shutdown ─────────────────────────────────────────────────
    logger.info("app.shutdown")


# ── Create App ───────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS (Environment Configured) ─────────────────────────────

origins = [origin.strip() for origin in settings.FRONTEND_CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routes ─────────────────────────────────────────────────

app.include_router(api_router)


# ── Health Check ─────────────────────────────────────────────────


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Returns API status and version info.",
)
async def health_check():
    """Root endpoint — confirms the API is running."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/docs",
    }
