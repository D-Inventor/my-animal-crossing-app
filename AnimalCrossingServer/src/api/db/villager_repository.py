from typing import Annotated, Protocol

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import get_session
from api.db.villager import Villager


class VillagerRepository(Protocol):
    async def get(self, id: str) -> Villager | None: ...
    async def update(self, villager: Villager) -> None: ...
    async def delete(self, villager: Villager) -> None: ...


class SessionVillagerRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: str) -> Villager | None:
        return await self._session.get(Villager, id)

    async def update(self, villager: Villager) -> None:
        self._session.add(villager)

    async def delete(self, villager: Villager) -> None:
        if villager in self._session:
            await self._session.delete(villager)


def get_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VillagerRepository:
    return SessionVillagerRepository(session)
