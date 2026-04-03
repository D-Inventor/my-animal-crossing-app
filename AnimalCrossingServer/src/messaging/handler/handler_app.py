import asyncio
import contextvars
import logging
from contextlib import AsyncExitStack
from typing import AsyncContextManager, AsyncIterable, Awaitable, Callable, Protocol

from .handler_endpoint_collection import HandlerEndpointCollection

logger = logging.getLogger(__name__)


class MessageDispatcher(Protocol):
    async def dispatch(self, command: object) -> None: ...


class MessageHandlerApp:
    def __init__(
        self,
        message_source: AsyncContextManager[AsyncIterable[object]],
        message_target: AsyncContextManager[MessageDispatcher],
        handler: Callable[..., Awaitable[list[object]]],
    ) -> None:
        self.message_source = message_source
        self.message_target = message_target
        self._handler_collection = HandlerEndpointCollection()
        self.handler = handler

    async def run(self) -> None:
        async with AsyncExitStack() as stack:
            target = await stack.enter_async_context(self.message_target)
            messages = await stack.enter_async_context(self.message_source)
            async for message in messages:
                try:
                    logger.info("received message %s", message)
                    ctx = contextvars.copy_context()

                    task = asyncio.create_task(self.handler(message), context=ctx)

                    responses = await task
                    for response in responses:
                        logger.info("dispatch message %s", response)
                        await target.dispatch(response)
                except Exception as error:
                    logger.error(
                        "Something went wrong while handling a message", exc_info=error
                    )
