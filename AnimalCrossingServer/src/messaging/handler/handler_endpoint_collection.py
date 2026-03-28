from typing import Callable, Self

from .handler_endpoint import HandlerEndpoint, MessageContext


class HandlerEndpointCollection:
    def __init__(self) -> None:
        self._endpoints: list[HandlerEndpoint] = []

    def add_handler(self, handler: HandlerEndpoint) -> Self:
        self._endpoints.append(handler)
        return self

    def add_handler_func(
        self,
        handler_func: Callable[..., None | object],
        message_filter: Callable[[object], bool] | None = None,
    ) -> Self:
        return self.add_handler(HandlerEndpoint.create(handler_func, message_filter))

    async def handle(self, message: object) -> list[object]:
        context = MessageContext()
        for endpoint in self._endpoints:
            await endpoint.handle(message, context)
        return context.published_messages()
