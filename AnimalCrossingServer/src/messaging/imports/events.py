import uuid

from pydantic import BaseModel


class VillagerSnapshotDownloadedEvent(BaseModel):
    saga_id: uuid.UUID
    snapshot_id: uuid.UUID
