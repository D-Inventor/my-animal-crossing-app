from enum import Enum


class MessageTopic(str, Enum):
    VILLAGERS = "villagers"
    IMPORT_EVENTS = "import_events"
    IMPORT_COMMANDS = "import_commands"
    IMPORT_ORCHESTRATOR_COMMANDS = "import_orchestrator_commands"


_registered_message_types = dict[type, MessageTopic]()


def map_to_topic(topic: MessageTopic):  # noqa: ANN201
    def decorator(cls):  # noqa: ANN001, ANN202
        _registered_message_types[cls] = topic
        return cls

    return decorator


def get_topic(message: object) -> MessageTopic:
    if message.__class__ not in _registered_message_types:
        raise ValueError(
            "The given type is not registered. "
            "Use the @map_to_topic decorator to register the type"
        )
    return _registered_message_types[message.__class__]
