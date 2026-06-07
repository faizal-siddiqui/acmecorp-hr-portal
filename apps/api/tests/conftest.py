import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.database import Base

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
async def db_session(mem_engine):
    factory = async_sessionmaker(mem_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
