import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.db.villager import Villager
from api.villagers.repository import SessionVillagerRepository


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_delete_villager(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given
    async with mariadb_session() as session:
        session.add(Villager(id="flg01", name="Ribbot"))
        await session.commit()

    # when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        villager = await repository.get("flg01")
        await repository.delete(villager)
        await session.commit()

    # then
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is None


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_do_nothing_when_delete_nonexistent_villager(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given: empty DB

    # when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        non_existent_villager = Villager(id="flg01", name="Ribbot")
        await repository.delete(non_existent_villager)
        await session.commit()

    # then: no error and DB is still empty
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result is None
