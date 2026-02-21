import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.app import app
from api.db.villager import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_delete_villager(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given
    async with mariadb_session() as session:
        session.add(Villager(id="flg01", name="Ribbot"))
        await session.commit()
    app.state._session_local = mariadb_session

    # When
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete("/villagers/flg01")

    # Then
    assert response.status_code == 204
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is None
