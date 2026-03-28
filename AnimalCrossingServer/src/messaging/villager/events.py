from pydantic import BaseModel

from messaging.topics import MessageTopic, map_to_topic


@map_to_topic(MessageTopic.VILLAGERS)
class VillagerCreated(BaseModel):
    id: str
