from uuid import uuid4

import pytest

from import_event_orchestrator.db.saga_state import SagaState, SagaStatus
from import_event_orchestrator.villager_import_orchestrator import (
    VillagerImportOrchestrator,
)
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from messaging.imports.events import VillagerSnapshotDownloadedEvent
from test.import_event_orchestrator.doubles import (
    InMemoryCommandDispatcher,
    InMemorySagaRepository,
)


class UnfamiliarMessage:
    pass


@pytest.mark.asyncio
async def test_should_create_saga_when_receiving_import_command() -> None:
    # given
    saga_repository = InMemorySagaRepository()
    command_dispatcher = InMemoryCommandDispatcher()
    orchestrator = VillagerImportOrchestrator(saga_repository, command_dispatcher)
    command_id = uuid4()
    command = ImportVillagersCommand(id=command_id)

    # when
    await orchestrator.handle(command)

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.id == command_id


@pytest.mark.asyncio
async def test_should_dispatch_download_snapshot_command_with_started_saga_id() -> None:
    # given
    saga_repository = InMemorySagaRepository()
    command_dispatcher = InMemoryCommandDispatcher()
    orchestrator = VillagerImportOrchestrator(saga_repository, command_dispatcher)
    command = ImportVillagersCommand(id=uuid4())

    # when
    await orchestrator.handle(command)

    # then
    assert command_dispatcher.dispatched_command is not None
    assert isinstance(
        command_dispatcher.dispatched_command, DownloadVillagerSnapshotCommand
    )
    assert command_dispatcher.dispatched_command.saga_id == command.id


@pytest.mark.asyncio
async def test_should_complete_saga_when_snapshot_downloaded_event_received() -> None:
    # given
    saga_repository = InMemorySagaRepository()
    command_dispatcher = InMemoryCommandDispatcher()
    orchestrator = VillagerImportOrchestrator(saga_repository, command_dispatcher)
    saga_id = uuid4()
    saga_repository.added_saga = SagaState.create(id=saga_id)
    event = VillagerSnapshotDownloadedEvent(saga_id=saga_id, snapshot_id=uuid4())

    # when
    await orchestrator.handle(event)

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.state == SagaStatus.COMPLETED


@pytest.mark.asyncio
async def test_should_ignore_unfamiliar_message_type() -> None:
    # given
    saga_repository = InMemorySagaRepository()
    command_dispatcher = InMemoryCommandDispatcher()
    orchestrator = VillagerImportOrchestrator(saga_repository, command_dispatcher)

    # when
    await orchestrator.handle(UnfamiliarMessage())

    # then
    assert saga_repository.added_saga is None
    assert command_dispatcher.dispatched_command is None


@pytest.mark.asyncio
async def test_should_not_fail_when_snapshot_downloaded_event_references_missing_saga() -> (
    None
):
    # given
    saga_repository = InMemorySagaRepository()
    command_dispatcher = InMemoryCommandDispatcher()
    orchestrator = VillagerImportOrchestrator(saga_repository, command_dispatcher)
    event = VillagerSnapshotDownloadedEvent(saga_id=uuid4(), snapshot_id=uuid4())

    # when
    await orchestrator.handle(event)

    # then
    assert True
