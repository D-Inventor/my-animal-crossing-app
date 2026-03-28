from aiokafka import AIOKafkaProducer

from messaging.topics import get_topic


class KafkaMessageDispatcher:
    def __init__(self, kafka: AIOKafkaProducer) -> None:
        self._kafka = kafka

    async def dispatch(self, command: object) -> None:
        await self._kafka.send(get_topic(command).value, command)
