import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, AsyncIterator

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from messaging.config import KafkaSettings
from messaging.serialize import create_default_serializer
from messaging.topics import MessageTopic

from .kafka_message_dispatcher import KafkaMessageDispatcher

logger = logging.getLogger(__name__)


@asynccontextmanager
async def create_kafka_producer() -> AsyncGenerator[KafkaMessageDispatcher, Any, None]:
    async with _create_producer() as producer:
        logger.debug("Kafka message dispatcher created")
        yield KafkaMessageDispatcher(producer)
    logger.debug("Kafka message dispatcher disposed")


@asynccontextmanager
async def create_kafka_consumer(
    topics: list[MessageTopic], group_id: str
) -> AsyncGenerator[AsyncIterator[object], Any, None]:
    async with _create_consumer(topics, group_id) as consumer:
        logger.debug("Kafka message consumer created")

        async def _read_messages() -> AsyncGenerator[object, Any, None]:
            async for message in consumer:
                yield message.value

        yield _read_messages()
    logger.debug("Kafka message consumer disposed")


def _create_producer() -> AIOKafkaProducer:
    kafka_settings = KafkaSettings()
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_settings.bootstrap_server,
        value_serializer=create_default_serializer().serialize,
        enable_idempotence=True,
    )
    return producer


def _create_consumer(topics: list[MessageTopic], group_id: str) -> AIOKafkaConsumer:
    kafka_settings = KafkaSettings()
    consumer = AIOKafkaConsumer(
        *[topic.value for topic in topics],
        bootstrap_servers=kafka_settings.bootstrap_server,
        group_id=group_id,
        value_deserializer=create_default_serializer().deserialize,
    )
    return consumer
