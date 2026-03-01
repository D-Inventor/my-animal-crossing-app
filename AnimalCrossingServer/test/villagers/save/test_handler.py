import pytest

from api.db.villager import Villager
from api.villagers.save import SaveVillagerRequest, endpoint
from test.villagers.in_memory_repository import InMemoryVillagerRepository
from test.villagers.in_memory_unit_of_work import InMemoryUnitOfWork


@pytest.mark.asyncio
async def test_should_create_new_villager():
    # given
    repository = InMemoryVillagerRepository()
    unit_of_work = InMemoryUnitOfWork([repository])

    # when
    await endpoint(
        "flg01", SaveVillagerRequest(name="Ribbot"), unit_of_work, repository
    )
    unit_of_work.flush()

    # then
    assert isinstance(await repository.get("flg01"), Villager)


@pytest.mark.asyncio
async def test_should_update_existing_villager():
    # given
    repository = InMemoryVillagerRepository()
    unit_of_work = InMemoryUnitOfWork([repository])
    await endpoint(
        "flg01", SaveVillagerRequest(name="Ribbot"), unit_of_work, repository
    )
    unit_of_work.flush()

    # when
    await endpoint(
        "flg01", SaveVillagerRequest(name="Ribbot 2.0"), unit_of_work, repository
    )

    # then
    result = await repository.get("flg01")
    assert isinstance(result, Villager)
    assert result.name == "Ribbot 2.0"
