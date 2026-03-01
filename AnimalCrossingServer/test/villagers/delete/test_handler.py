import pytest

from api.db.villager import Villager
from api.villagers.delete import endpoint
from test.villagers.in_memory_repository import InMemoryVillagerRepository
from test.villagers.in_memory_unit_of_work import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_should_delete_villager():
    # given
    repository = InMemoryVillagerRepository()
    unit_of_work = InMemoryUnitOfWork([repository])
    await repository.update(Villager(id="flg01", name="Ribbot"))
    await unit_of_work.save()
    unit_of_work.flush()

    # when
    await endpoint("flg01", unit_of_work, repository)
    unit_of_work.flush()

    # then
    result = await repository.get("flg01")
    assert result is None


@pytest.mark.asyncio
async def test_should_do_nothing_when_delete_nonexistent_villager():
    # given
    repository = InMemoryVillagerRepository()
    unit_of_work = InMemoryUnitOfWork([repository])

    # when
    await endpoint("flg01", unit_of_work, repository)
    unit_of_work.flush()

    # then: no error and repository is still empty
    result = await repository.get("flg01")
    assert result is None
