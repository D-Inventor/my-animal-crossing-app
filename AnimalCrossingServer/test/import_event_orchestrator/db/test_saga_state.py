from import_event_orchestrator.db.saga_state import SagaState, SagaStatus


def test_should_create_saga_with_initial_values() -> None:
    # when
    saga = SagaState.create()

    # then
    assert saga.id is not None
    assert saga.state == SagaStatus.STARTED
    assert saga.completed_steps == []
    assert saga.data == {}
