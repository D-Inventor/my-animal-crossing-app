from uuid import uuid4

import pytest

from import_event_orchestrator.villager_import_orchestrator import (
    VillagerImportOrchestrator,
)
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from test.import_event_orchestrator.doubles import (
    InMemoryCommandDispatcher,
    InMemorySagaRepository,
)


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
