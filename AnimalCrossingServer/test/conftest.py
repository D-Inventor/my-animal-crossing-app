from typing import AsyncGenerator

import httpx
import pytest
from sqlalchemy import NullPool, make_url
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.mysql import MySqlContainer

from test.api_mock import ApiMock


@pytest.fixture(scope="session")
async def mariadb_engine():
    with MySqlContainer("mariadb:12.2") as mysql:
        connection_url = make_url(mysql.get_connection_url()).set(
            drivername="mysql+aiomysql"
        )
        engine = create_async_engine(connection_url, poolclass=NullPool, echo=False)
        yield engine
        await engine.dispose()


@pytest.fixture()
def api() -> ApiMock:
    return ApiMock()


@pytest.fixture()
async def client(api: ApiMock) -> AsyncGenerator[httpx.AsyncClient]:
    transport = httpx.MockTransport(api.handle)
    async with httpx.AsyncClient(
        transport=transport, base_url="https://api.example.test"
    ) as http_client:
        yield http_client
