"""Pytest configuration and shared fixtures."""

from pathlib import Path
from typing import AsyncGenerator, Tuple

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import URL, Connection, NullPool, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.mysql import MySqlContainer

from api.db import Base


async def _setup_mariadb_container_async() -> AsyncGenerator[
    Tuple[async_sessionmaker, URL, AsyncEngine], None
]:
    with MySqlContainer("mariadb:12.2") as mysql:
        connection_url = make_url(mysql.get_connection_url()).set(
            drivername="mysql+aiomysql"
        )
        engine = create_async_engine(connection_url, poolclass=NullPool, echo=False)
        session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
        yield session_local, connection_url, engine
        await engine.dispose()


@pytest.fixture
async def mariadb_session() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async for (
        session_local,
        _,
        engine,
    ) in _setup_mariadb_container_async():
        # Create all tables using async context
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield session_local
        break


def run_migrations(connection: Connection, cfg: Config) -> None:
    cfg.attributes["connection"] = connection
    command.upgrade(cfg, "head")


@pytest.fixture
async def mariadb_with_migrations() -> AsyncGenerator[async_sessionmaker, None]:
    async for (
        session_local,
        connection_url,
        engine,
    ) in _setup_mariadb_container_async():
        # Configure and run alembic migrations
        # Convert async URL to sync for alembic (alembic uses sync connections)
        alembic_cfg = Config()
        alembic_cfg.set_main_option(
            "sqlalchemy.url",
            connection_url.render_as_string(hide_password=False).replace("%", "%%"),
        )
        # Point to the alembic migrations directory
        alembic_dir = Path(__file__).parent.parent / "src" / "api" / "alembic"
        alembic_cfg.set_main_option("script_location", str(alembic_dir))

        async with engine.begin() as conn:
            await conn.run_sync(run_migrations, alembic_cfg)

        yield session_local
