import copy

from api.db.villager import Villager


class InMemoryVillagerRepository:
    def __init__(self):
        self._persisted_villagers: dict[str, Villager] = {}
        self._fetched_villagers: dict[str, Villager] = {}
        self._deleted_villagers: set[str] = set()

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

    async def delete(self, villager: Villager) -> None:
        if villager.id not in self._fetched_villagers:
            raise ValueError("Cannot delete a villager that was not fetched")
        self._deleted_villagers.add(villager.id)

    async def save(self) -> None:
        for id, villager in self._fetched_villagers.items():
            self._persisted_villagers[id] = copy.deepcopy(villager)

        for id in self._deleted_villagers:
            self._persisted_villagers.pop(id, None)

    def flush(self) -> None:
        self._fetched_villagers = {}
        self._deleted_villagers = set()
