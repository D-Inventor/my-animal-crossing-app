import uuid

from pydantic import BaseModel

from messaging.topics import MessageTopic, map_to_topic


@map_to_topic(MessageTopic.IMPORT_EVENTS)
class VillagerSnapshotDownloadedEvent(BaseModel):
    saga_id: uuid.UUID
    snapshot_id: uuid.UUID
