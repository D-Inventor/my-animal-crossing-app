import uuid

from pydantic import BaseModel

from messaging.topics import MessageTopic, map_to_topic


@map_to_topic(MessageTopic.IMPORT_COMMANDS)
class ImportVillagersCommand(BaseModel):
    id: uuid.UUID


@map_to_topic(MessageTopic.IMPORT_COMMANDS)
class DownloadVillagerSnapshotCommand(BaseModel):
    saga_id: uuid.UUID
