"""Pytest configuration and shared fixtures."""

from typing import Generator, Tuple

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.mysql import MySqlContainer

from api.db import Base


@pytest.fixture
def mariadb_session() -> Generator[Tuple[sessionmaker, str], None, None]:
    """Start a MariaDB container.

    Yields:
        (sessionmaker, connection_url): A tuple containing a sessionmaker
        for the container DB and the connection URL.
    """
    with MySqlContainer("mariadb:10.11") as mysql:
        connection_url = mysql.get_connection_url().replace(
            "mysql://", "mysql+pymysql://"
        )
        engine = create_engine(connection_url, echo=False)
        Base.metadata.create_all(engine)
        session_local = sessionmaker(bind=engine, expire_on_commit=False)
        yield session_local, connection_url
