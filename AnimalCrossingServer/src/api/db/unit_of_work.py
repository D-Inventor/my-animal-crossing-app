import itertools
from typing import Annotated, Any, AsyncGenerator, Awaitable, Callable, Protocol, Self

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.db.event_handler import EventHandler, get_event_handler_collection_from_app
from api.db.session import get_session
from api.db.villager import Villager, VillagerCreated


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
    def __init__(
        self,
        session: AsyncSession,
        event_handler: EventHandler,
    ) -> None:
        self._session = session
        self._event_handler = event_handler
        self.finished = False

    async def save(self) -> None:
        await self._session.commit()
        self.finished = True
        all_events = list(
            itertools.chain(
                *[
                    entity.consume_events()
                    for entity in self._session.identity_map.values()
                    if isinstance(entity, Villager)
                ]
            )
        )
        await self._event_handler(all_events)

    async def rollback(self) -> None:
        await self._session.rollback()
        self.finished = True

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:  # noqa: ANN002
        if not self.finished:
            self.rollback()


async def get_unit_of_work(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[UnitOfWork, None]:
    event_handler = get_event_handler_collection_from_app(request.app)
    async with SessionUnitOfWork(session, event_handler.publish) as unit_of_work:
        yield unit_of_work
