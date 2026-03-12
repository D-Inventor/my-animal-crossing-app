from typing import Protocol

from import_event_orchestrator.db.saga_repository import SagaRepository
from import_event_orchestrator.db.saga_state import SagaState
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)


class CommandDispatcher(Protocol):
    async def dispatch(self, command: object) -> None: ...


class VillagerImportOrchestrator:
    def __init__(
        self,
        saga_repository: SagaRepository,
        command_dispatcher: CommandDispatcher,
    ) -> None:
        self.saga_repository = saga_repository
        self.command_dispatcher = command_dispatcher

    async def handle(self, command: ImportVillagersCommand) -> None:
        saga = SagaState.create(id=command.id)
        await self.saga_repository.add(saga)
        await self.command_dispatcher.dispatch(
            DownloadVillagerSnapshotCommand(saga_id=saga.id)
        )
