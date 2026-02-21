import pytest

from api.db.villager import Villager
from api.villagers.delete import endpoint
from test.villagers.in_memory_repository import InMemoryVillagerRepository


@pytest.mark.asyncio
async def test_should_delete_villager():
    # given
    repository = InMemoryVillagerRepository()
    await repository.update(Villager(id="flg01", name="Ribbot"))
    await repository.save()
    repository.flush()

    # when
    await endpoint("flg01", repository)
    repository.flush()

    # then
    result = await repository.get("flg01")
    assert result is None


@pytest.mark.asyncio
async def test_should_do_nothing_when_delete_nonexistent_villager():
    # given
    repository = InMemoryVillagerRepository()

    # when
    await endpoint("flg01", repository)
    repository.flush()

    # then: no error and repository is still empty
    result = await repository.get("flg01")
    assert result is None
