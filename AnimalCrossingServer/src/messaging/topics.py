from enum import Enum


class MessageTopic(str, Enum):
    VILLAGERS = "villagers"
    IMPORT_EVENTS = "import_events"
    IMPORT_COMMANDS = "import_commands"
