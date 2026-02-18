import uuid

from api.db import Villager


def test_should_persist_villager_with_alembic_migrations(mariadb_with_migrations):
    """Test that a villager persists using alembic-created schema.

    Given: a MariaDB container with schema created via alembic migrations
    When: we save a Villager instance
    Then: we can retrieve it from the DB with correct data
    """
    # Given: a MariaDB container with alembic migrations applied
    session_local = mariadb_with_migrations

    # When: we save a Villager instance
    villager_id = f"villager-{uuid.uuid4()}"
    with session_local() as session:
        session.add(Villager(id=villager_id, name="Sherb"))
        session.commit()

    # Then: we can retrieve the same villager from the DB
    with session_local() as session:
        got = session.get(Villager, villager_id)
        assert got is not None
        assert got.id == villager_id
        assert got.name == "Sherb"
