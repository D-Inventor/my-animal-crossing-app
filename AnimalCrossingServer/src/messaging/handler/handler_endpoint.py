import asyncio
import inspect
from typing import Awaitable, Callable, TypeVar


class _SkipArgument:
    pass


_SKIP_ARGUMENT = _SkipArgument()

HandlerFunc = Callable[..., None | object]
AsyncHandlerFunc = Callable[..., Awaitable[None | object]]


class MessageContext:
    def __init__(self) -> None:
        self._messages: list[object] = []

    def publish(self, message: object) -> None:
        self._messages.append(message)

    def published_messages(self) -> list[object]:
        return list(self._messages)


class HandlerEndpoint:
    def __init__(
        self,
        handler_invoker: Callable[[object, MessageContext], None | object]
        | Callable[[object, MessageContext], Awaitable[None | object]],
        message_filter: Callable[[object], bool],
    ) -> None:
        self._handler_invoker = handler_invoker
        self._message_filter = message_filter

    async def handle(self, message: object, context: MessageContext) -> None:
        if self._message_filter(message):
            result = await self._handler_invoker(message, context)
            if result is not None:
                context.publish(result)

    @classmethod
    def create(
        cls,
        handler_func: HandlerFunc | AsyncHandlerFunc,
        message_filter: Callable[[object], bool] | None = None,
    ) -> HandlerEndpoint:
        return cls(
            _create_handler_invoker(handler_func),
            message_filter
            if message_filter is not None
            else _create_filter_from_handler_signature(handler_func),
        )


def _create_filter_from_handler_signature(
    handler_func: HandlerFunc | AsyncHandlerFunc,
) -> Callable[[object], bool]:
    params = list(inspect.signature(handler_func).parameters.values())
    if not params:
        raise ValueError
    first_param = params[0]
    if first_param.annotation is inspect.Parameter.empty:
        raise ValueError
    message_type = first_param.annotation
    return lambda m: isinstance(m, message_type)


def _create_parameter_resolver(
    param: inspect.Parameter,
) -> Callable[[object, MessageContext], object | _SkipArgument]:
    if param.annotation is MessageContext:
        return lambda _, context: context
    if param.default is not inspect.Parameter.empty:
        return lambda _, __: _SKIP_ARGUMENT
    raise ValueError


def _create_handler_invoker(
    handler_func: HandlerFunc | AsyncHandlerFunc,
) -> Callable[[object, MessageContext], Awaitable[None | object]]:
    params = list(inspect.signature(handler_func).parameters.values())
    parameter_resolvers = [_create_parameter_resolver(param) for param in params[1:]]

    async_handler: AsyncHandlerFunc = (
        handler_func
        if inspect.iscoroutinefunction(handler_func)
        else _make_async(handler_func)
    )

    def invoke(message: object, context: MessageContext) -> Awaitable[None | object]:
        args: list[object] = [message]
        for resolver in parameter_resolvers:
            resolved = resolver(message, context)
            if resolved is _SKIP_ARGUMENT:
                continue
            args.append(resolved)
        return async_handler(*args)

    return invoke


T = TypeVar("T")


def _make_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    def wrapper(*args, **kwargs) -> Awaitable[T]:  # noqa: ANN002, ANN003
        return asyncio.to_thread(func, *args, **kwargs)

    return wrapper


def accept_all_messages(_: object) -> bool:
    return True
