import uuid

from fastapi.testclient import TestClient
from sqlalchemy import URL, make_url

from api.app import app
from api.db import Villager


def test_should_fetch_villager_by_name_integration(mariadb_session):
    # Given: a MariaDB container with schema (via fixture)
    session_local, connection_url = mariadb_session

    # Insert a villager into the DB
    villager_id = f"villager-{uuid.uuid4()}"
    with session_local() as session:
        session.add(Villager(id=villager_id, name="Bob"))
        session.commit()

    # When: calling the API endpoint with the test DB URL
    app.state.database_url = make_url(connection_url)
    client = TestClient(app)
    resp = client.get("/villagers/by-name/Bob")

    # Then: expecting 200 and the villager payload
    assert resp.status_code == 200
    data = resp.json()
    assert data == {"data": [{"id": villager_id, "name": "Bob"}]}
