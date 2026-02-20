import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from api.app import app
from api.db import Villager


@pytest.mark.asyncio
async def test_should_fetch_villager_by_name_integration(mariadb_session):
    # Given: a MariaDB container with schema (via fixture)
    session_local, connection_url = mariadb_session

    # Insert a villager into the DB
    villager_id = f"villager-{uuid.uuid4()}"
    async with session_local() as session:
        session.add(Villager(id=villager_id, name="Bob"))
        await session.commit()

    # When: calling the API endpoint with the test DB URL
    # Store the sessionmaker in app state so the route reuses the same connection
    app.state._session_local = session_local
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.get("/villagers/by-name/Bob")

    # Then: expecting 200 and the villager payload
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"data": [{"id": villager_id, "name": "Bob"}]}
