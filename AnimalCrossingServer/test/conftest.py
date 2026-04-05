import pytest
from sqlalchemy import NullPool, make_url
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.mysql import MySqlContainer


@pytest.fixture(scope="session")
async def mariadb_engine():
    with MySqlContainer("mariadb:12.2") as mysql:
        connection_url = make_url(mysql.get_connection_url()).set(
            drivername="mysql+aiomysql"
        )
        engine = create_async_engine(connection_url, poolclass=NullPool, echo=False)
        yield engine
        await engine.dispose()
