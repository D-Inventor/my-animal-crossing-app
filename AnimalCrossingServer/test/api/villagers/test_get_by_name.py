import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from api.app_builder import AppBuilder
from api.db import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_fetch_villager_by_name(
    mariadb_reset_engine: AsyncEngine,
):
    # give
    mariadb_session = async_sessionmaker(
        bind=mariadb_reset_engine, expire_on_commit=False
    )
    villager_id = "flg01"
    async with mariadb_session() as session:
        session.add(Villager(id=villager_id, name="Ribbot"))
        await session.commit()
    app = AppBuilder().add_database_engine(lambda: mariadb_reset_engine).build()

    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/villagers/by-name/Ribbot")

    # Then: expecting 200 and the villager payload
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"data": [{"id": villager_id, "name": "Ribbot"}]}
