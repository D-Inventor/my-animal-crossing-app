import uuid

from pydantic import BaseModel


class ImportVillagersCommand(BaseModel):
    id: uuid.UUID


class DownloadVillagerSnapshotCommand(BaseModel):
    saga_id: uuid.UUID
