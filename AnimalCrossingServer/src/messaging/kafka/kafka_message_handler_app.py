import asyncio
from typing import Self

from messaging.handler import bootstrap_signals
from messaging.handler.handler_app import MessageHandlerApp
from messaging.handler.handler_endpoint_collection import HandlerEndpointCollection
from messaging.kafka.dependency import create_kafka_consumer, create_kafka_producer
from messaging.topics import MessageTopic


class KafkaMessageHandlerApp(HandlerEndpointCollection):
    def __init__(self, group_id: str) -> None:
        super().__init__()
        self._topics: list[MessageTopic] = []
        self.group_id = group_id

    def add_topics(self, topics: list[MessageTopic]) -> Self:
        self._topics.extend(topics)
        return self

    async def run(self) -> None:
        await bootstrap_signals(
            asyncio.get_running_loop(),
            asyncio.create_task(
                MessageHandlerApp(
                    create_kafka_consumer(self._topics, self.group_id),
                    create_kafka_producer(),
                    self.handle,
                ).run()
            ),
        )
