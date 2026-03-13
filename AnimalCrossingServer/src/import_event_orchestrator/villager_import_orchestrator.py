from typing import Protocol

from import_event_orchestrator.db.saga_repository import SagaRepository
from import_event_orchestrator.db.saga_state import SagaState, SagaStatus
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from messaging.imports.events import VillagerSnapshotDownloadedEvent


class CommandDispatcher(Protocol):
    async def dispatch(self, command: object) -> None: ...


class VillagerImportOrchestrator:
    def __init__(
        self, saga_repository: SagaRepository, command_dispatcher: CommandDispatcher
    ) -> None:
        self.saga_repository = saga_repository
        self.command_dispatcher = command_dispatcher

    async def handle(self, message: object) -> None:
        match message:
            case ImportVillagersCommand() as command:
                await self._handle_import_villagers_command(command)
            case VillagerSnapshotDownloadedEvent() as event:
                await self._handle_villager_snapshot_downloaded_event(event)
            case _:
                return

    async def _handle_import_villagers_command(
        self, command: ImportVillagersCommand
    ) -> None:
        saga = SagaState.create(id=command.id)
        await self.saga_repository.add(saga)
        await self.command_dispatcher.dispatch(
            DownloadVillagerSnapshotCommand(saga_id=saga.id)
        )

    async def _handle_villager_snapshot_downloaded_event(
        self, event: VillagerSnapshotDownloadedEvent
    ) -> None:
        saga = await self.saga_repository.get(event.saga_id)
        if saga is None:
            return
        saga.state = SagaStatus.COMPLETED
