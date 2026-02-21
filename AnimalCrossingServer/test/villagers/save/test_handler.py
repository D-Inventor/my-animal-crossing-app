import copy

import pytest

from api.db.villager import Villager
from api.villagers.save import SaveVillagerRequest, endpoint


class InMemoryVillagerRepository:
    def __init__(self):
        self._persisted_villagers: dict[str, Villager] = {}
        self._fetched_villagers: dict[str, Villager] = {}

    async def get(self, id: str) -> Villager | None:
        if id in self._fetched_villagers:
            return self._fetched_villagers[id]
        if id in self._persisted_villagers:
            villager = copy.deepcopy(self._persisted_villagers[id])
            self._fetched_villagers[id] = villager
            return villager
        return None

    async def update(self, villager: Villager) -> None:
        if (
            villager.id in self._fetched_villagers
            and villager is not self._fetched_villagers[villager.id]
        ):
            raise ValueError("Updates must be made on the fetched villager instance")
        if (
            villager.id not in self._fetched_villagers
            and villager.id in self._persisted_villagers
        ):
            raise ValueError("Cannot update a villager that was not fetched")
        self._fetched_villagers[villager.id] = villager

    async def save(self) -> None:
        for id, villager in self._fetched_villagers.items():
            self._persisted_villagers[id] = copy.deepcopy(villager)

    def flush(self) -> None:
        self._fetched_villagers = {}


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
