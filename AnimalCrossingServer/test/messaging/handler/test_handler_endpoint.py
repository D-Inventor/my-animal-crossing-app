import pytest

from messaging.handler import (
    HandlerEndpoint,
    MessageContext,
    accept_all_messages,
)


class TestMessage:
    pass


class OtherMessage:
    pass


@pytest.mark.asyncio
async def test_should_call_handler_func_with_matching_message() -> None:
    # given
    received_messages: list[TestMessage] = []
    message = TestMessage()
    context = MessageContext()

    def handler_func(received_message: TestMessage) -> None:
        received_messages.append(received_message)

    endpoint = HandlerEndpoint.create(handler_func)

    # when
    await endpoint.handle(message, context)

    # then
    assert received_messages == [message]


@pytest.mark.asyncio
async def test_should_not_call_handler_func_for_unmatched_message_type() -> None:
    # given
    received_messages: list[OtherMessage] = []
    context = MessageContext()

    def handler_func(received_message: OtherMessage) -> None:
        received_messages.append(received_message)

    endpoint = HandlerEndpoint.create(handler_func)

    # when
    await endpoint.handle(TestMessage(), context)

    # then
    assert received_messages == []


@pytest.mark.asyncio
async def test_should_use_custom_filter_to_skip_handler_func() -> None:
    # given
    received_messages: list[object] = []
    context = MessageContext()

    def handler_func(received_message: object) -> None:
        received_messages.append(received_message)

    endpoint = HandlerEndpoint.create(
        handler_func, message_filter=lambda m: isinstance(m, TestMessage)
    )

    # when
    await endpoint.handle(OtherMessage(), context)

    # then
    assert received_messages == []


@pytest.mark.asyncio
async def test_should_await_async_handler_functions() -> None:
    # given
    received_messages: list[object] = []

    async def async_handler_func(received_message: object) -> None:
        received_messages.append(received_message)

    endpoint = HandlerEndpoint.create(
        async_handler_func, message_filter=accept_all_messages
    )

    # when
    await endpoint.handle(OtherMessage(), MessageContext())

    # then
    assert len(received_messages) == 1


@pytest.mark.asyncio
async def test_should_dispatch_handler_func_return_value() -> None:
    # given
    reply = OtherMessage()
    context = MessageContext()

    def handler_func(_: TestMessage) -> OtherMessage:
        return reply

    endpoint = HandlerEndpoint.create(handler_func)

    # when
    await endpoint.handle(TestMessage(), context)

    # then
    assert context.published_messages() == [reply]


@pytest.mark.asyncio
async def test_should_not_dispatch_when_handler_func_returns_none() -> None:
    # given
    context = MessageContext()

    def handler_func(_: TestMessage) -> None:
        return None

    endpoint = HandlerEndpoint.create(handler_func)

    # when
    await endpoint.handle(TestMessage(), context)

    # then
    assert context.published_messages() == []


@pytest.mark.asyncio
async def test_should_pass_message_context_to_handler_func_when_expected() -> None:
    # given
    received_contexts: list[MessageContext] = []
    default_context = MessageContext()
    context = MessageContext()

    def handler_func(
        _: TestMessage,
        received_context: MessageContext = default_context,
    ) -> None:
        received_contexts.append(received_context)

    endpoint = HandlerEndpoint.create(handler_func)

    # when
    await endpoint.handle(TestMessage(), context)

    # then
    assert received_contexts == [context]


def test_should_raise_when_handler_func_has_no_type_annotation() -> None:
    # given / when / then
    with pytest.raises(ValueError):
        HandlerEndpoint.create(lambda m: None)


def test_should_create_message_context_with_empty_messages_by_default() -> None:
    # given / when
    context = MessageContext()

    # then
    assert context.published_messages() == []


def test_should_accept_all_messages_returns_true_for_any_message() -> None:
    # given
    message = OtherMessage()

    # when / then
    assert accept_all_messages(message) is True
