"""API dependencies for CiteReady."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session.

    Used as a FastAPI dependency for endpoints that require DB access.
    """
    async with async_session() as session:
        yield session
