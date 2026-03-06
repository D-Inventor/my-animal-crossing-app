import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.db.villager import Villager
from api.villagers.repository import SessionVillagerRepository


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_insert_new_villager(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given: empty DB

    # when
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
async def test_should_update_existing_villager(
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
        villager.name = "Ribbot Updated"
        await repository.update(villager)
        await session.commit()

    # then
    async with mariadb_session() as session:
        result = await session.get(Villager, "flg01")
        assert result.name == "Ribbot Updated"
