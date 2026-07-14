"""SQLAlchemy database engine and session management.

Uses SQLite (async via aiosqlite) for development.
Switch DATABASE_URL to PostgreSQL for production.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# ── Database Engine ──────────────────────────────────────────────

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.LOG_LEVEL == "DEBUG",
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def init_db() -> None:
    """Create all tables if they don't exist."""
    # Import models here to ensure they are registered with Base before create_all
    from app.models import analysis  # noqa

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
