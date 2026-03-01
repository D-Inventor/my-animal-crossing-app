from test.villagers.in_memory_repository import TestRepositoryProtocol


class InMemoryUnitOfWork:
    def __init__(self, repositories: list[TestRepositoryProtocol]):
        self._repositories = repositories

    async def save(self) -> None:
        for repository in self._repositories:
            repository.save()

    def flush(self) -> None:
        for repository in self._repositories:
            repository.flush()
