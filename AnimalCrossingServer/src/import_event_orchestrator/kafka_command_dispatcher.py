from aiokafka import AIOKafkaProducer

from messaging.topics import MessageTopic


class KafkaCommandDispatcher:
    def __init__(self, kafka: AIOKafkaProducer) -> None:
        self._kafka = kafka

    async def dispatch(self, command: object) -> None:
        await self._kafka.send(MessageTopic.IMPORT_COMMANDS.value, command)
