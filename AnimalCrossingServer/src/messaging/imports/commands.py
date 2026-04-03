import uuid

from pydantic import BaseModel

from messaging import MessageTopic, message


@message(MessageTopic.IMPORT_ORCHESTRATOR_COMMANDS)
class ImportVillagersCommand(BaseModel):
    id: uuid.UUID


@message(MessageTopic.IMPORT_COMMANDS)
class DownloadVillagerSnapshotCommand(BaseModel):
    saga_id: uuid.UUID
