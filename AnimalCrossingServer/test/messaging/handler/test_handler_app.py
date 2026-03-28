from typing import AsyncIterable

import pytest

from messaging.handler import MessageHandlerApp


class ExampleMessage:
    pass


class FakeMessageSource:
    def __init__(self, messages: list[object]):
        self.messages = messages
        self.has_opened: bool = False
        self.has_closed: bool = False

    async def __aenter__(self) -> AsyncIterable[object]:
        self.has_opened = True

        async def to_async_iterator():
            for message in self.messages:
                yield message

        return to_async_iterator()

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.has_closed = True


class FakeMessageDispatcher:
    def __init__(self):
        self.messages: list[object] = []

    async def dispatch(self, message: object):
        self.messages.append(message)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class FakeHandler:
    def __init__(self, return_value: list[object] | None = None):
        self.handled_messages: list[object] = []
        self.return_value = return_value if return_value is not None else []

    async def handle(self, message: object):
        self.handled_messages.append(message)
        return self.return_value


@pytest.mark.asyncio
async def test_should_handle_message_from_source():
    # given
    handler = FakeHandler()
    message_source = FakeMessageSource([ExampleMessage()])
    message_app = MessageHandlerApp(
        message_source,
        FakeMessageDispatcher(),
        handler.handle,
    )

    # when
    await message_app.run()

    # then
    assert len(handler.handled_messages) == 1
    assert isinstance(handler.handled_messages[0], ExampleMessage)
    assert message_source.has_opened
    assert message_source.has_closed


@pytest.mark.asyncio
async def test_should_dispatch_result_messages_to_target():
    # given
    message_source = FakeMessageSource([ExampleMessage()])
    message_dispatcher = FakeMessageDispatcher()
    message_app = MessageHandlerApp(
        message_source, message_dispatcher, FakeHandler([ExampleMessage()]).handle
    )

    # when
    await message_app.run()

    # then
    assert len(message_dispatcher.messages) == 1
    assert isinstance(message_dispatcher.messages[0], ExampleMessage)
