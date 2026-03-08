from typing import Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .saga_state import SagaState


class SagaRepository(Protocol):
    async def get(self, saga_id: UUID) -> SagaState | None: ...

    async def add(self, saga: SagaState) -> None: ...


class SessionSagaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, saga_id: UUID) -> SagaState | None:
        return await self.session.get(SagaState, saga_id)

    async def add(self, saga: SagaState) -> None:
        self.session.add(saga)
        await self.session.flush()
