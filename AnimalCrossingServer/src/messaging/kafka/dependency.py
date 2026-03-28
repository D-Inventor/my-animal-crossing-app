import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator

from messaging.kafka.kafka_message_dispatcher import KafkaMessageDispatcher
from messaging.topics import MessageTopic

from .consumer import create_consumer
from .producer import create_producer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def create_kafka_producer() -> AsyncGenerator[KafkaMessageDispatcher, Any, None]:
    async with create_producer() as producer:
        logger.debug("Kafka message dispatcher created")
        yield KafkaMessageDispatcher(producer)
    logger.debug("Kafka message dispatcher disposed")


@asynccontextmanager
async def create_kafka_consumer(
    topics: list[MessageTopic], group_id: str
) -> AsyncGenerator[AsyncIterator[object], Any, None]:
    async with create_consumer(topics, group_id) as consumer:
        logger.debug("Kafka message consumer created")

        async def _read_messages() -> AsyncGenerator[object, Any, None]:
            async for message in consumer:
                yield message.value

        yield _read_messages()
    logger.debug("Kafka message consumer disposed")
