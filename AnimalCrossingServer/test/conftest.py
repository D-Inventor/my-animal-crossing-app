"""Pytest configuration and shared fixtures."""

from pathlib import Path
from typing import AsyncGenerator

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, NullPool, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.mysql import MySqlContainer

from api.db import Base


@pytest.fixture(scope="session")
async def mariadb_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a single MariaDB container for the entire test session."""
    with MySqlContainer("mariadb:12.2") as mysql:
        connection_url = make_url(mysql.get_connection_url()).set(
            drivername="mysql+aiomysql"
        )
        engine = create_async_engine(connection_url, poolclass=NullPool, echo=False)
        yield engine
        await engine.dispose()


@pytest.fixture
async def mariadb_session(
    mariadb_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Reset tables before each test and provide a fresh sessionmaker."""
    # Drop and recreate all tables for this test
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_local = async_sessionmaker(bind=mariadb_engine, expire_on_commit=False)
    yield session_local


def run_migrations(connection: Connection, cfg: Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture
async def mariadb_with_migrations(
    mariadb_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Reset tables and run migrations before each test."""
    # Drop all tables first
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Configure alembic for this test
    alembic_cfg = Config()
    connection_url = mariadb_engine.url.render_as_string(hide_password=False).replace(
        "%", "%%"
    )
    alembic_cfg.set_main_option("sqlalchemy.url", connection_url)
    alembic_dir = Path(__file__).parent.parent / "src" / "api" / "db" / "alembic"
    alembic_cfg.set_main_option("script_location", str(alembic_dir))

    # Run migrations
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(run_migrations, alembic_cfg)

    session_local = async_sessionmaker(bind=mariadb_engine, expire_on_commit=False)
    yield session_local
