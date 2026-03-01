import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.app import create_app
from api.db import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_fetch_villager_by_name(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # give
    villager_id = "flg01"
    async with mariadb_session() as session:
        session.add(Villager(id=villager_id, name="Ribbot"))
        await session.commit()
    app = create_app()

    app.state._session_local = mariadb_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/villagers/by-name/Ribbot")

    # Then: expecting 200 and the villager payload
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"data": [{"id": villager_id, "name": "Ribbot"}]}
