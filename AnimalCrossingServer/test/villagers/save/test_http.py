import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.app import app
from api.db.villager import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_create_new_villager(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # Given
    app.state._session_local = mariadb_session

    # When
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.put("/villagers/flg01", json={"name": "Ribbot"})

    # Then
    async with mariadb_session() as session:
        stmt = select(Villager)
        result = (await session.scalars(stmt)).one()
        assert result.name == "Ribbot"
        assert result.id == "flg01"
