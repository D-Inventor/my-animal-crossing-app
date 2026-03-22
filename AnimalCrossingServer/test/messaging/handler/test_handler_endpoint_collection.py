import pytest

from messaging.handler.handler_endpoint import HandlerEndpoint
from messaging.handler.handler_endpoint_collection import HandlerEndpointCollection


class TestMessage:
    pass


class OtherMessage:
    pass


class ResultA:
    pass


class ResultB:
    pass


@pytest.mark.asyncio
async def test_should_create_context_and_invoke_assigned_handler_endpoint() -> None:
    # given
    received_messages: list[TestMessage] = []

    def handler_func(msg: TestMessage) -> None:
        received_messages.append(msg)

    collection = HandlerEndpointCollection([HandlerEndpoint.create(handler_func)])
    message = TestMessage()

    # when
    await collection.handle(message)

    # then
    assert received_messages == [message]


@pytest.mark.asyncio
async def test_should_publish_all_messages_from_multiple_handlers() -> None:
    # given
    def handler_a(msg: TestMessage) -> ResultA:
        return ResultA()

    def handler_b(msg: TestMessage) -> ResultB:
        return ResultB()

    collection = HandlerEndpointCollection(
        [
            HandlerEndpoint.create(handler_a),
            HandlerEndpoint.create(handler_b),
        ]
    )

    # when
    context = await collection.handle(TestMessage())

    # then
    published = context.published_messages()
    assert any(isinstance(m, ResultA) for m in published)
    assert any(isinstance(m, ResultB) for m in published)
    assert len(published) == 2
