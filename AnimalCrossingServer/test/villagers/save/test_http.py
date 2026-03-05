import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from api.app_builder import AppBuilder
from api.db.session import get_sessionmaker_for_app
from api.db.villager import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_create_new_villager(
    mariadb_reset_engine: AsyncEngine,
):
    # Given
    app = AppBuilder().add_database_engine(lambda: mariadb_reset_engine).build()

    # When
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.put("/villagers/flg01", json={"name": "Ribbot"})

    # Then
    mariadb_session = get_sessionmaker_for_app(app)
    async with mariadb_session() as session:
        stmt = select(Villager)
        result = (await session.scalars(stmt)).one()
        assert result.name == "Ribbot"
        assert result.id == "flg01"
