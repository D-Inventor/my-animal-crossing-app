from typing import Annotated, AsyncGenerator, Protocol, Self

from fastapi import Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.db.session import get_session


class UnitOfWork(Protocol):
    """
    A custom unit of work implementation allows me
    to add additional logic when saving changes.

    In this case that's necessary to send event signals to kafka asynchronously,
    because the event system of sql alchemy is inherently non-synchronous.
    """

    async def save() -> None: ...
    async def rollback() -> None: ...


class SessionUnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.finished = False

    async def save(self) -> None:
        await self._session.commit()
        self.finished = True

    async def rollback(self) -> None:
        await self._session.rollback()
        self.finished = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:  # noqa: ANN002
        if not self.finished:
            self.rollback()


async def get_unit_of_work(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[UnitOfWork, None]:
    async with SessionUnitOfWork(session) as unit_of_work:
        yield unit_of_work
