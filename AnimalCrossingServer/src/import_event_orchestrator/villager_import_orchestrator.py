import logging

from import_event_orchestrator.db.saga_repository import SagaRepository
from import_event_orchestrator.db.saga_state import SagaState, SagaStatus
from messaging.handler import MessageContext
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from messaging.imports.events import (
    VillagerSnapshotDownloadedEvent,
    VillagerSnapshotDownloadFailedEvent,
)

logger = logging.getLogger(__name__)


class VillagerImportOrchestrator:
    def __init__(self, saga_repository: SagaRepository) -> None:
        self.saga_repository = saga_repository

    async def handle(self, message: object, context: MessageContext) -> None:
        match message:
            case ImportVillagersCommand() as command:
                await self._handle_import_villagers_command(command, context)
            case VillagerSnapshotDownloadedEvent() as event:
                await self._handle_villager_snapshot_downloaded_event(event)
            case VillagerSnapshotDownloadFailedEvent() as event:
                await self._handle_villager_snapshot_download_failed_event(event)
            case _:
                self._log_ignored_message(message)

    async def _handle_import_villagers_command(
        self, command: ImportVillagersCommand, context: MessageContext
    ) -> None:
        saga = SagaState.create(id=command.id)
        await self.saga_repository.add(saga)
        context.publish(DownloadVillagerSnapshotCommand(saga_id=saga.id))
        logger.debug("started import saga %s", command.id)

    async def _handle_villager_snapshot_downloaded_event(
        self, event: VillagerSnapshotDownloadedEvent
    ) -> None:
        saga = await self.saga_repository.get(event.saga_id)
        if saga is None:
            logger.debug(
                "ignored snapshot downloaded event for missing saga %s",
                event.saga_id,
            )
            return
        saga.state = SagaStatus.COMPLETED
        logger.debug("completed import saga %s", event.saga_id)

    async def _handle_villager_snapshot_download_failed_event(
        self, event: VillagerSnapshotDownloadFailedEvent
    ) -> None:
        saga = await self.saga_repository.get(event.saga_id)
        if saga is None:
            logger.debug(
                "ignored download failed event for missing saga %s", event.saga_id
            )
            return
        saga.state = SagaStatus.FAILED
        logger.debug("failed import saga %s", event.saga_id)

    def _log_ignored_message(self, message: object) -> None:
        logger.debug("ignored unknown message: %s", type(message).__name__)
