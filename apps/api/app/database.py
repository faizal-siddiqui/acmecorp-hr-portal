"""
Async SQLAlchemy 2.0 engine + session factory.

URL routing:
  sqlite+aiosqlite://  → dev / test  (file or :memory:)
  postgresql+asyncpg:// → production  (Postgres)

The public surface used by the rest of the app:
  Base              — declarative base; all models inherit from this
  engine            — the shared async engine (app-lifetime)
  AsyncSessionLocal — session factory (expire_on_commit=False suits async)
  get_db            — FastAPI dependency that yields an AsyncSession
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


def engine_kwargs(url: str) -> dict[str, Any]:
    """Return dialect-specific keyword arguments for create_async_engine."""
    if url.startswith("sqlite"):
        # aiosqlite requires check_same_thread=False when used outside the
        # creating thread (e.g. inside async tasks / pytest-asyncio).
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    **engine_kwargs(settings.database_url),
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a transactional AsyncSession per request."""
    async with AsyncSessionLocal() as session:
        yield session
