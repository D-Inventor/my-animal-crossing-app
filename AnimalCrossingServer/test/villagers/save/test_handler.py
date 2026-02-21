import pytest

from api.db.villager import Villager
from api.villagers.save import SaveVillagerRequest, endpoint
from test.villagers.in_memory_repository import InMemoryVillagerRepository


@pytest.mark.asyncio
async def test_should_create_new_villager():
    # given
    repository = InMemoryVillagerRepository()

    # when
    await endpoint("flg01", SaveVillagerRequest(name="Ribbot"), repository)
    repository.flush()

    # then
    assert isinstance(await repository.get("flg01"), Villager)


@pytest.mark.asyncio
async def test_should_update_existing_villager():
    # given
    repository = InMemoryVillagerRepository()
    await endpoint("flg01", SaveVillagerRequest(name="Ribbot"), repository)
    repository.flush()

    # when
    await endpoint("flg01", SaveVillagerRequest(name="Ribbot 2.0"), repository)

    # then
    result = await repository.get("flg01")
    assert isinstance(result, Villager)
    assert result.name == "Ribbot 2.0"
