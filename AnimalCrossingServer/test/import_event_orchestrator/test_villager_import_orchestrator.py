import logging
from uuid import uuid4

import pytest

from import_event_orchestrator.db.saga_state import SagaState, SagaStatus
from import_event_orchestrator.villager_import_orchestrator import (
    VillagerImportOrchestrator,
    finish_download,
)
from messaging.handler import MessageContext
from messaging.imports.commands import (
    CreateDiffWithActiveSnapshotCommand,
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
    MigrateActiveVillagerSetCommand,
)
from messaging.imports.events import (
    DiffCreatedEvent,
    VillagerSnapshotDownloadedEvent,
    VillagerSnapshotDownloadFailedEvent,
)
from test.import_event_orchestrator.doubles import (
    InMemorySagaRepository,
)

LOGGER_NAME = "import_event_orchestrator.villager_import_orchestrator"


class UnfamiliarMessage:
    pass


def create_orchestrator() -> tuple[
    InMemorySagaRepository,
    VillagerImportOrchestrator,
]:
    saga_repository = InMemorySagaRepository()
    orchestrator = VillagerImportOrchestrator(saga_repository)
    return saga_repository, orchestrator


def captured_messages(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [record.message for record in caplog.records]


@pytest.mark.asyncio
async def test_should_create_saga_when_receiving_import_command() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    command_id = uuid4()
    command = ImportVillagersCommand(id=command_id)

    # when
    await orchestrator.handle(command, MessageContext())

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.id == command_id


@pytest.mark.asyncio
async def test_should_dispatch_download_snapshot_command_with_started_saga_id() -> None:
    # given
    _, orchestrator = create_orchestrator()
    context = MessageContext()
    command = ImportVillagersCommand(id=uuid4())

    # when
    await orchestrator.handle(command, context)

    # then
    published_message = next(iter(context.published_messages()))
    assert published_message is not None
    assert isinstance(published_message, DownloadVillagerSnapshotCommand)
    assert published_message.saga_id == command.id


@pytest.mark.asyncio
async def test_should_start_diff_when_snapshot_downloaded_event_received() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    saga_id = uuid4()
    saga_repository.added_saga = SagaState.create(id=saga_id)
    event = VillagerSnapshotDownloadedEvent(saga_id=saga_id, snapshot_id=uuid4())
    message_context = MessageContext()

    # when
    await orchestrator.handle(event, message_context)

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.state == SagaStatus.STARTED
    assert saga_repository.added_saga.completed_steps == ["download_snapshot"]
    assert saga_repository.added_saga.data == {"snapshot_id": event.snapshot_id}
    assert isinstance(
        message_context.published_messages()[0], CreateDiffWithActiveSnapshotCommand
    )


@pytest.mark.asyncio
async def test_should_ignore_unfamiliar_message_type() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    context = MessageContext()

    # when
    await orchestrator.handle(UnfamiliarMessage(), context)

    # then
    assert saga_repository.added_saga is None
    assert len(context.published_messages()) == 0


@pytest.mark.asyncio
async def test_should_handle_missing_saga_gracefully_on_finished_download() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    event = VillagerSnapshotDownloadedEvent(saga_id=uuid4(), snapshot_id=uuid4())
    context = MessageContext()

    # when
    await orchestrator.handle(event, context)

    # then
    assert saga_repository.added_saga is None
    assert len(context.published_messages()) == 0


@pytest.mark.asyncio
async def test_should_mark_saga_as_failure_when_download_fails() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    saga_id = uuid4()
    saga_repository.added_saga = SagaState.create(id=saga_id)
    event = VillagerSnapshotDownloadFailedEvent(saga_id=saga_id, snapshot_id=uuid4())

    # when
    await orchestrator.handle(event, MessageContext())

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.state == SagaStatus.FAILED


@pytest.mark.asyncio
async def test_should_handle_missing_saga_gracefully_on_failed_download() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    event = VillagerSnapshotDownloadFailedEvent(saga_id=uuid4())
    context = MessageContext()

    # when
    await orchestrator.handle(event, context)

    # then
    assert saga_repository.added_saga is None


@pytest.mark.asyncio
async def test_should_complete_saga_when_diff_detects_no_changes() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    saga = SagaState.create()
    finish_download(saga, snapshot_id=uuid4())
    saga_repository.added_saga = saga

    # when
    await orchestrator.handle(
        DiffCreatedEvent(saga_id=saga.id, diff_id=uuid4(), differences_found=False),
        MessageContext(),
    )

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.state == SagaStatus.COMPLETED
    assert saga_repository.added_saga.completed_steps == [
        "download_snapshot",
        "create_diff",
    ]


@pytest.mark.asyncio
async def test_should_send_modify_command_when_diff_detects_changes() -> None:
    # given
    saga_repository, orchestrator = create_orchestrator()
    saga = SagaState.create()
    finish_download(saga, snapshot_id=uuid4())
    saga_repository.added_saga = saga
    context = MessageContext()

    # when
    await orchestrator.handle(
        DiffCreatedEvent(saga_id=saga.id, diff_id=uuid4(), differences_found=True),
        context,
    )

    # then
    assert saga_repository.added_saga is not None
    assert saga_repository.added_saga.state == SagaStatus.STARTED
    assert saga_repository.added_saga.completed_steps == [
        "download_snapshot",
        "create_diff",
    ]
    assert isinstance(context.published_messages()[0], MigrateActiveVillagerSetCommand)
