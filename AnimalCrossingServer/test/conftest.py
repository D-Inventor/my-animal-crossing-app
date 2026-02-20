"""Pytest configuration and shared fixtures."""

from pathlib import Path
from typing import AsyncGenerator, Tuple

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.mysql import MySqlContainer

from api.db import Base


async def _setup_mariadb_container_async() -> AsyncGenerator[
    Tuple[async_sessionmaker, str, AsyncEngine], None
]:
    """Set up MariaDB container with async engine and sessionmaker.

    Yields:
        (sessionmaker, connection_url, engine): A tuple containing the sessionmaker,
        connection URL, and async engine for the container DB.
    """
    with MySqlContainer("mariadb:10.11") as mysql:
        connection_url = mysql.get_connection_url().replace(
            "mysql://", "mysql+aiomysql://"
        )
        engine = create_async_engine(connection_url, echo=False)
        session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
        yield session_local, connection_url, engine
        await engine.dispose()


@pytest.fixture
async def mariadb_session() -> AsyncGenerator[Tuple[async_sessionmaker, str], None]:
    """Start a MariaDB container with async session support.

    Yields:
        (sessionmaker, connection_url): A tuple containing an async sessionmaker
        for the container DB and the connection URL.
    """
    async for (
        session_local,
        connection_url,
        _engine,
    ) in _setup_mariadb_container_async():
        # Create all tables using async context
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield session_local, connection_url
        break


def run_migrations(connection: Connection, cfg: Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture
async def mariadb_with_migrations() -> AsyncGenerator[async_sessionmaker, None]:
    """Start a MariaDB container with alembic migrations applied.

    Yields:
        sessionmaker: An async sessionmaker for the container DB.
    """
    async for (
        session_local,
        connection_url,
        engine,
    ) in _setup_mariadb_container_async():
        # Configure and run alembic migrations
        # Convert async URL to sync for alembic (alembic uses sync connections)
        alembic_cfg = Config()
        alembic_cfg.set_main_option("sqlalchemy.url", connection_url)
        # Point to the alembic migrations directory
        alembic_dir = Path(__file__).parent.parent / "src" / "api" / "alembic"
        alembic_cfg.set_main_option("script_location", str(alembic_dir))

        async with engine.begin() as conn:
            await conn.run_sync(run_migrations, alembic_cfg)

        yield session_local
