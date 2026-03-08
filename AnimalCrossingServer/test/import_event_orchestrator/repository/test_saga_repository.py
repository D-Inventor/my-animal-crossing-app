"""Tests for SagaRepository implementation."""

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from import_event_orchestrator.db.saga_repository import SessionSagaRepository
from import_event_orchestrator.db.saga_state import SagaState, SagaStatus


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_add_saga_state_to_database(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    # given
    saga_id = uuid4()
    saga = SagaState(
        id=saga_id,
        state=SagaStatus.STARTED,
        completed_steps=[],
        data={},
    )

    # when
    async with session_maker() as when_session:
        repository = SessionSagaRepository(when_session)
        await repository.add(saga)
        await when_session.commit()

    # then
    async with session_maker() as then_session:
        retrieved_saga = await then_session.get(SagaState, saga_id)
        assert retrieved_saga is not None
        assert retrieved_saga.id == saga_id
        assert retrieved_saga.state == SagaStatus.STARTED
        assert retrieved_saga.completed_steps == []
        assert retrieved_saga.data == {}


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_get_persisted_saga_state(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    # given
    saga_id = uuid4()
    saga = SagaState(
        id=saga_id,
        state=SagaStatus.STARTED,
        completed_steps=["step_1", "step_2"],
        data={"key": "value"},
    )
    async with session_maker() as given_session:
        given_session.add(saga)
        await given_session.commit()

    # when
    async with session_maker() as when_session:
        repository = SessionSagaRepository(when_session)
        retrieved_saga = await repository.get(saga_id)

    # then
    assert retrieved_saga is not None
    assert retrieved_saga.id == saga_id
    assert retrieved_saga.state == SagaStatus.STARTED
    assert retrieved_saga.completed_steps == ["step_1", "step_2"]
    assert retrieved_saga.data == {"key": "value"}
