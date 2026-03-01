from typing import Any, Awaitable, Callable

from fastapi import FastAPI

from api.db.villager import VillagerCreated

EventHandler = Callable[[list[VillagerCreated]], Awaitable[Any]]


class EventHandlerCollection:
    def __init__(self) -> None:
        self._handlers: list[EventHandler] = []

    def subscribe(self, handler: EventHandler) -> None:
        self._handlers.append(handler)

    async def publish(self, events: list[VillagerCreated]) -> None:
        for handler in self._handlers:
            await handler(events)


def get_event_handler_collection_from_app(app: FastAPI) -> EventHandlerCollection:
    key = "_event_handler_collection"
    if not hasattr(app.state, key):
        app.state[key] = EventHandlerCollection()

    return app.state[key]
