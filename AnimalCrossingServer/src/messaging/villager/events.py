from pydantic import BaseModel

from messaging import MessageTopic, message


@message(MessageTopic.VILLAGERS)
class VillagerCreated(BaseModel):
    id: str
