from uuid import UUID

from import_event_orchestrator.db.saga_state import SagaState


class InMemorySagaRepository:
    def __init__(self) -> None:
        self.added_saga: SagaState | None = None

    async def get(self, saga_id: UUID) -> SagaState | None:
        if self.added_saga is None:
            return None
        return self.added_saga if self.added_saga.id == saga_id else None

    async def add(self, saga: SagaState) -> None:
        self.added_saga = saga


class InMemoryCommandDispatcher:
    def __init__(self) -> None:
        self.dispatched_command: object | None = None

    async def dispatch(self, command: object) -> None:
        self.dispatched_command = command
