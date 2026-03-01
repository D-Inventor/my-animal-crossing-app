import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.db import Villager


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_persist_villager_with_alembic_migrations(
    mariadb_with_migrations: async_sessionmaker[AsyncSession],
):
    """Test that a villager persists using alembic-created schema.

    Given: a MariaDB container with schema created via alembic migrations
    When: we save a Villager instance
    Then: we can retrieve it from the DB with correct data
    """
    # Given: a MariaDB container with alembic migrations applied

    # When: we save a Villager instance
    villager_id = f"villager-{uuid.uuid4()}"
    async with mariadb_with_migrations() as session:
        session.add(Villager(id=villager_id, name="Sherb"))
        await session.commit()

    # Then: we can retrieve the same villager from the DB
    async with mariadb_with_migrations() as session:
        result = await session.get(Villager, villager_id)
        assert result is not None
        assert result.id == villager_id
        assert result.name == "Sherb"
