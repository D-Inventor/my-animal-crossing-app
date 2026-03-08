from typing import AsyncGenerator

import pytest
from aiokafka import AIOKafkaProducer
from testcontainers.kafka import KafkaContainer

from messaging.migrate import install_topics
from messaging.serialize import create_default_serializer


@pytest.fixture
async def kafka_container() -> AsyncGenerator[KafkaContainer, None]:
    with KafkaContainer(image="confluentinc/cp-kafka:8.0.4").with_kraft() as kafka:
        await install_topics(kafka.get_bootstrap_server())
        yield kafka


@pytest.fixture
async def kafka_producer(
    kafka_container: KafkaContainer,
) -> AsyncGenerator[AIOKafkaProducer, None]:
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_serializer=create_default_serializer().serialize,
        enable_idempotence=True,
    )
    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()
