from typing import AsyncGenerator

import pytest
from sqlalchemy import NullPool, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.mysql import MySqlContainer

from import_event_orchestrator.db.saga_state import Base


@pytest.fixture(scope="session")
async def mariadb_engine() -> AsyncGenerator[AsyncEngine, None]:
    with MySqlContainer("mariadb:12.2") as mysql:
        connection_url = make_url(mysql.get_connection_url()).set(
            drivername="mysql+aiomysql"
        )
        engine = create_async_engine(connection_url, poolclass=NullPool, echo=False)
        yield engine
        await engine.dispose()


@pytest.fixture
async def mariadb_reset_engine(
    mariadb_engine: AsyncEngine,
) -> AsyncGenerator[AsyncEngine, None]:
    async with mariadb_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield mariadb_engine


@pytest.fixture
async def session_maker(
    mariadb_reset_engine: AsyncEngine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create a session maker for tests."""
    session_local = async_sessionmaker(
        bind=mariadb_reset_engine, expire_on_commit=False
    )
    yield session_local


@pytest.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for a single test."""
    async with session_maker() as session_instance:
        yield session_instance
