from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from import_event_orchestrator.app import process_message
from import_event_orchestrator.db.saga_repository import SessionSagaRepository
from import_event_orchestrator.db.saga_state import SagaState
from messaging.handler import MessageContext
from messaging.imports.commands import ImportVillagersCommand


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_persist_saga_when_import_command_received(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    # given
    command_id = uuid4()
    command = ImportVillagersCommand(id=command_id)

    # when
    async with session_maker() as session:
        await process_message(
            command, MessageContext(), session, SessionSagaRepository(session)
        )

    # then
    async with session_maker() as session:
        saga = await session.get(SagaState, command_id)
        assert saga is not None
