import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api.db.villager import Villager
from api.db.villager_repository import SessionVillagerRepository


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_get_villager_when_exists(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given
    async with mariadb_session() as session:
        session.add(Villager(id="flg01", name="Ribbot"))
        await session.commit()

    # when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        result = await repository.get("flg01")

    # then
    assert result == Villager(id="flg01", name="Ribbot")


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_get_none_when_not_exists(
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given: empty DB

    # when
    async with mariadb_session() as session:
        repository = SessionVillagerRepository(session)
        result = await repository.get("flg01")

    # then
    assert result is None
