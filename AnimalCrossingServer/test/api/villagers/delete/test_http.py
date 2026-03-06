import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from api.app_builder import AppBuilder
from api.db.villager import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_delete_villager(
    mariadb_reset_engine: AsyncEngine,
):
    # given
    mariadb_session = async_sessionmaker(
        bind=mariadb_reset_engine, expire_on_commit=False
    )
    async with mariadb_session() as session:
        session.add(Villager(id="flg01", name="Ribbot"))
        await session.commit()
    app = AppBuilder().add_database_engine(lambda: mariadb_reset_engine).build()

    # When
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.delete("/villagers/flg01")

    # Then
    assert response.status_code == 204
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is None
