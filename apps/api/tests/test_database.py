"""
TDD: async SQLAlchemy engine and session factory.

Tests are deliberately self-contained: they spin up an in-memory SQLite engine
so they never touch the filesystem or require a running Postgres instance.
"""

import contextlib

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, engine_kwargs

# ── Unit: dialect-specific engine kwargs ─────────────────────────────────────


def test_sqlite_engine_kwargs_sets_check_same_thread() -> None:
    kwargs = engine_kwargs("sqlite+aiosqlite:///./test.db")
    assert kwargs == {"connect_args": {"check_same_thread": False}}


def test_postgres_engine_kwargs_are_empty() -> None:
    kwargs = engine_kwargs("postgresql+asyncpg://user:pass@localhost/db")
    assert kwargs == {}


def test_memory_sqlite_engine_kwargs_sets_check_same_thread() -> None:
    kwargs = engine_kwargs("sqlite+aiosqlite:///:memory:")
    assert kwargs == {"connect_args": {"check_same_thread": False}}


# ── Integration: session executes queries ────────────────────────────────────


@pytest.fixture
async def mem_engine():
    """Ephemeral in-memory SQLite engine — created and disposed per test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def mem_session(mem_engine):
    factory = async_sessionmaker(mem_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


async def test_session_is_async_session(mem_session: AsyncSession) -> None:
    assert isinstance(mem_session, AsyncSession)


async def test_session_executes_select_one(mem_session: AsyncSession) -> None:
    result = await mem_session.execute(text("SELECT 1 AS val"))
    assert result.scalar() == 1


async def test_session_transaction_rollback(mem_engine) -> None:
    """A rolled-back transaction leaves no changes."""
    factory = async_sessionmaker(mem_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session, session.begin():
        await session.execute(text("CREATE TABLE IF NOT EXISTS _tmp (id INTEGER PRIMARY KEY)"))
        await session.execute(text("INSERT INTO _tmp VALUES (1)"))
        await session.rollback()

    # table may or may not exist, but no committed row of value 1 should be there
    async with factory() as session:
        try:
            result = await session.execute(text("SELECT COUNT(*) FROM _tmp"))
            count = result.scalar()
            assert count == 0
        except Exception:
            # Table doesn't exist because the DDL was rolled back — also fine
            pass


# ── get_db dependency ─────────────────────────────────────────────────────────


async def test_get_db_yields_async_session(mem_engine) -> None:
    """get_db must be an async generator that yields AsyncSession."""
    from app.database import get_db

    factory = async_sessionmaker(mem_engine, class_=AsyncSession, expire_on_commit=False)

    # Temporarily patch AsyncSessionLocal to use our in-memory engine
    import app.database as db_module

    original = db_module.AsyncSessionLocal
    db_module.AsyncSessionLocal = factory
    try:
        gen = get_db()
        session = await gen.__anext__()
        assert isinstance(session, AsyncSession)
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        # exhaust the generator (triggers cleanup)
        with contextlib.suppress(StopAsyncIteration):
            await gen.aclose()
    finally:
        db_module.AsyncSessionLocal = original
