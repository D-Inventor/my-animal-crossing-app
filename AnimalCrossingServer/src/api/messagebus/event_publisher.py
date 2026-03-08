from aiokafka import AIOKafkaProducer

from api.db.villager import VillagerCreated
from messaging.topics import MessageTopic


class EventPublisher:
    def __init__(self, kafka: AIOKafkaProducer) -> None:
        self._kafka = kafka

    async def publish(self, events: list[VillagerCreated]) -> None:
        for event in events:
            await self._kafka.send(MessageTopic.VILLAGERS.value, event)
