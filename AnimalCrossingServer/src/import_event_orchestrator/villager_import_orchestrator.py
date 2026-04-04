import logging
import uuid

from import_event_orchestrator.db.saga_repository import SagaRepository
from import_event_orchestrator.db.saga_state import SagaState, SagaStatus
from messaging.handler import MessageContext
from messaging.imports.commands import (
    CreateDiffWithActiveSnapshotCommand,
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from messaging.imports.events import (
    DiffCreatedEvent,
    VillagerSnapshotDownloadedEvent,
    VillagerSnapshotDownloadFailedEvent,
)

logger = logging.getLogger(__name__)


class VillagerImportOrchestrator:
    def __init__(self, saga_repository: SagaRepository) -> None:
        self.saga_repository = saga_repository

    async def handle(self, message: object, context: MessageContext) -> None:

        if isinstance(message, ImportVillagersCommand):
            await self._handle_import_villagers_command(message, context)
            return

        saga_id = get_saga_id(message)
        if saga_id is None:
            log_no_saga_id()
            return

        saga = await self.saga_repository.get(saga_id)
        if saga is None:
            log_saga_not_found(saga_id)
            return

        match message:
            case VillagerSnapshotDownloadedEvent() as event:
                self._handle_villager_snapshot_downloaded_event(event, context, saga)
            case VillagerSnapshotDownloadFailedEvent() as event:
                self._handle_villager_snapshot_download_failed_event(event, saga)
            case DiffCreatedEvent() as event:
                self._handle_diff_created_event(event, saga)
            case _:
                log_message_unfamiliar(saga.id, type(message).__name__)

    async def _handle_import_villagers_command(
        self, command: ImportVillagersCommand, context: MessageContext
    ) -> None:
        saga = SagaState.create(id=command.id)
        await self.saga_repository.add(saga)
        context.publish(DownloadVillagerSnapshotCommand(saga_id=saga.id))
        log_start_import(command)

    def _handle_villager_snapshot_downloaded_event(
        self,
        event: VillagerSnapshotDownloadedEvent,
        context: MessageContext,
        saga: SagaState,
    ) -> None:
        finish_download(saga, event.snapshot_id)
        context.publish(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=saga.id, snapshot_id=event.snapshot_id
            )
        )
        log_download_event(event)

    def _handle_villager_snapshot_download_failed_event(
        self, event: VillagerSnapshotDownloadFailedEvent, saga: SagaState
    ) -> None:
        saga.state = SagaStatus.FAILED
        log_download_failed_event(event.saga_id)

    def _handle_diff_created_event(
        self, event: DiffCreatedEvent, saga: SagaState
    ) -> None:
        finish_diff(saga)
        log_saga_completed(saga.id)


def finish_download(saga: SagaState, snapshot_id: uuid.UUID) -> None:
    saga.data["snapshot_id"] = snapshot_id
    saga.completed_steps.append("download_snapshot")


def finish_diff(saga: SagaState) -> None:
    saga.state = SagaStatus.COMPLETED
    saga.completed_steps.append("create_diff")


def get_saga_id(message: object) -> uuid.UUID | None:
    return (
        message.saga_id
        if hasattr(message, "saga_id") and isinstance(message.saga_id, uuid.UUID)
        else None
    )


def log_no_saga_id() -> None:
    logger.warning("message has not saga_id. message ignored")


def log_saga_not_found(saga_id: uuid.UUID) -> None:
    logger.warning("saga %s not found. message ignored", saga_id)


def log_start_import(saga_id: uuid.UUID) -> None:
    logger.info("saga %s started", saga_id)


def log_download_event(saga_id: uuid.UUID) -> None:
    logger.debug("snapshot downloaded for saga %s", saga_id)


def log_download_failed_event(saga_id: uuid.UUID) -> None:
    logger.debug("snapshot download failed for saga %s", saga_id)


def log_saga_completed(saga_id: uuid.UUID) -> None:
    logger.info("saga %s finished", saga_id)


def log_message_unfamiliar(saga_id: uuid.UUID, message_type: str) -> None:
    logger.warning(
        "cannot handle %s for saga %s. message is unfamiliar", message_type, saga_id
    )
