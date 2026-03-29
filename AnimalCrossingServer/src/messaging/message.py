from .serialize import map_to_serializer
from .topics import MessageTopic, map_to_topic


def message(topic: MessageTopic):  # noqa: ANN201
    topic_decorator = map_to_topic(topic)
    serializer_decorator = map_to_serializer()

    def decorator(cls):  # noqa: ANN001, ANN202
        topic_decorator(cls)
        serializer_decorator(cls)
        return cls

    return decorator
