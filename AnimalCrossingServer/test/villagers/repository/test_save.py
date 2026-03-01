import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.db.villager import Villager
from api.villagers.repository import SessionVillagerRepository


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_persist_villager_to_db(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given / when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        await repository.update(Villager(id="flg01", name="Ribbot"))
        await session.commit()

    # then
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is not None


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_not_persist_without_save(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given / when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        await repository.update(Villager(id="flg01", name="Ribbot"))
        # no save called

    # then
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is None
