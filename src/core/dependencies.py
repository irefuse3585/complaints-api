"""
src/core/dependencies.py

Async SQLAlchemy engine and session factory using the new async_sessionmaker,
plus FastAPI dependency for providing a database session to route handlers.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (  # noqa: E501
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..config import settings

# Create the async engine using the DATABASE_URL from settings
engine = create_async_engine(
    settings.database_url,
    echo=True,  # Log SQL for debugging; disable or set to False in production
    future=True,  # Use SQLAlchemy 2.0 API
)

# Use async_sessionmaker to create AsyncSession instances correctly
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Do not expire objects after commit
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession and ensures cleanup.

    Yields:
        AsyncSession: a database session tied to the request lifecycle.
    """
    async with AsyncSessionLocal() as session:
        yield session
