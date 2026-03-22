import inspect
from typing import Callable


class _SkipArgument:
    pass


_SKIP_ARGUMENT = _SkipArgument()


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
        handler_invoker: Callable[[object, MessageContext], None | object],
        message_filter: Callable[[object], bool],
    ) -> None:
        self._handler_invoker = handler_invoker
        self._message_filter = message_filter

    async def handle(self, message: object, context: MessageContext) -> None:
        if self._message_filter(message):
            result = self._handler_invoker(message, context)
            if result is not None:
                context.publish(result)

    @classmethod
    def create(
        cls,
        handler_func: Callable[..., None | object],
        message_filter: Callable[[object], bool] | None = None,
    ) -> HandlerEndpoint:
        return cls(
            _create_handler_invoker(handler_func),
            message_filter
            if message_filter is not None
            else _create_filter_from_handler_signature(handler_func),
        )


def _create_filter_from_handler_signature(
    handler_func: Callable[..., None | object],
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
    handler_func: Callable[..., None | object],
) -> Callable[[object, MessageContext], None | object]:
    params = list(inspect.signature(handler_func).parameters.values())
    parameter_resolvers = [_create_parameter_resolver(param) for param in params[1:]]

    def invoke(message: object, context: MessageContext) -> None | object:
        args: list[object] = [message]
        for resolver in parameter_resolvers:
            resolved = resolver(message, context)
            if resolved is _SKIP_ARGUMENT:
                continue
            args.append(resolved)
        return handler_func(*args)

    return invoke


def accept_all_messages(_: object) -> bool:
    return True
