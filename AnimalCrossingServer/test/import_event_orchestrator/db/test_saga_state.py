from uuid import uuid4

from import_event_orchestrator.db.saga_state import SagaState, SagaStatus


def test_should_create_saga_with_initial_values() -> None:
    # when
    saga = SagaState.create()

    # then
    assert saga.id is not None
    assert saga.state == SagaStatus.STARTED
    assert saga.completed_steps == []
    assert saga.data == {}


def test_should_create_saga_with_provided_id() -> None:
    # given
    custom_id = uuid4()

    # when
    saga = SagaState.create(id=custom_id)

    # then
    assert saga.id == custom_id
