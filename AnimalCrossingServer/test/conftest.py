"""Pytest configuration and shared fixtures."""

from pathlib import Path
from typing import Generator, Tuple

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from api.db import Base


def _setup_mariadb_container() -> Generator[
    Tuple[sessionmaker, str, object], None, None
]:
    """Set up MariaDB container with engine and sessionmaker.

    Yields:
        (sessionmaker, connection_url, engine): A tuple containing the sessionmaker,
        connection URL, and engine for the container DB.
    """
    with MySqlContainer("mariadb:10.11") as mysql:
        connection_url = mysql.get_connection_url().replace(
            "mysql://", "mysql+pymysql://"
        )
        engine = create_engine(connection_url, echo=False)
        session_local = sessionmaker(bind=engine, expire_on_commit=False)
        yield session_local, connection_url, engine


@pytest.fixture
def mariadb_session() -> Generator[Tuple[sessionmaker, str], None, None]:
    """Start a MariaDB container.

    Yields:
        (sessionmaker, connection_url): A tuple containing a sessionmaker
        for the container DB and the connection URL.
    """
    for session_local, connection_url, engine in _setup_mariadb_container():
        Base.metadata.create_all(engine)
        yield session_local, connection_url


@pytest.fixture
def mariadb_with_migrations() -> Generator[sessionmaker, None, None]:
    """Start a MariaDB container with alembic migrations applied.

    Yields:
        sessionmaker: A sessionmaker for the container DB.
    """
    for session_local, connection_url, engine in _setup_mariadb_container():
        # Configure and run alembic migrations
        alembic_cfg = Config()
        alembic_cfg.set_main_option("sqlalchemy.url", connection_url)
        # Point to the alembic migrations directory
        alembic_dir = Path(__file__).parent.parent / "src" / "api" / "alembic"
        alembic_cfg.set_main_option("script_location", str(alembic_dir))

        # Run migrations
        command.upgrade(alembic_cfg, "head")

        yield session_local
