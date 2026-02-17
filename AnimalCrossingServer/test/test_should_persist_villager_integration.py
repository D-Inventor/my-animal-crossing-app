import uuid

from api.db import Villager


def test_should_persist_villager_integration(mariadb_session):
    # Given: a MariaDB container with schema (via fixture)
    session_local, _ = mariadb_session

    # When: we save a Villager instance
    villager_id = f"villager-{uuid.uuid4()}"
    with session_local() as session:
        session.add(Villager(id=villager_id, name="Bob"))
        session.commit()

    # Then: we can retrieve the same villager from the DB
    with session_local() as session:
        got = session.get(Villager, villager_id)
        assert got is not None
        assert got.id == villager_id
        assert got.name == "Bob"
