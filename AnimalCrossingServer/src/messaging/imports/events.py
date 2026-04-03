import uuid

from pydantic import BaseModel

from messaging import MessageTopic, message


@message(MessageTopic.IMPORT_EVENTS)
class VillagerSnapshotDownloadedEvent(BaseModel):
    saga_id: uuid.UUID
    snapshot_id: uuid.UUID


@message(MessageTopic.IMPORT_EVENTS)
class VillagerSnapshotDownloadFailedEvent(BaseModel):
    saga_id: uuid.UUID
