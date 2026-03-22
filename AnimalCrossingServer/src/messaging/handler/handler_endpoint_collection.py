from typing import Sequence
from .handler_endpoint import HandlerEndpoint, MessageContext


class HandlerEndpointCollection:
    def __init__(self, endpoints: Sequence[HandlerEndpoint]) -> None:
        self._endpoints = list(endpoints)

    async def handle(self, message: object) -> MessageContext:
        context = MessageContext()
        for endpoint in self._endpoints:
            await endpoint.handle(message, context)
        return context
