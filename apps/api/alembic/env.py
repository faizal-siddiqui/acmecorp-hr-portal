"""
Alembic env.py — async-compatible migration runner.

Supports both SQLite (dev/test) and Postgres (prod) via DATABASE_URL.
render_as_batch=True is required for SQLite, which does not support
ALTER TABLE natively; it is safe and a no-op on Postgres.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine import Connection

from app.config import settings
from app.database import Base
from app import models  # noqa: F401

# Make alembic's logging config take effect if present
alembic_config = context.config
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# Metadata from all models — models must be imported before this is used.
target_metadata = Base.metadata


def _get_url() -> str:
    return settings.database_url


# ── Offline mode (generates SQL without a live connection) ────────────────────


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (connects and applies migrations) ─────────────────────────────


def _run_migrations_sync(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    url = _get_url()
    connectable = create_async_engine(url)
    async with connectable.connect() as connection:
        await connection.run_sync(_run_migrations_sync)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
