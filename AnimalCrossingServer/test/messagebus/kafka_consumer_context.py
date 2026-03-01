from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiokafka import AIOKafkaConsumer
from pydantic_core import from_json
from testcontainers.kafka import KafkaContainer


@asynccontextmanager
async def kafka_consumer(
    kafka_container: KafkaContainer, topic: str
) -> AsyncGenerator[AIOKafkaConsumer, None]:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_deserializer=lambda m: from_json(m),
        auto_offset_reset="earliest",
    )
    try:
        await consumer.start()
        yield consumer
    finally:
        await consumer.stop()
