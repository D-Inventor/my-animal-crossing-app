"""Pytest configuration for eventbus tests."""

import json
from typing import AsyncGenerator

import pytest
from aiokafka import AIOKafkaProducer
from testcontainers.kafka import KafkaContainer


@pytest.fixture
async def kafka_container() -> AsyncGenerator[KafkaContainer, None]:
    """Create a Kafka container for eventbus tests."""
    kafka = KafkaContainer()
    kafka.start()
    yield kafka
    kafka.stop()


@pytest.fixture
async def kafka_producer(
    kafka_container: KafkaContainer,
) -> AsyncGenerator[AIOKafkaProducer, None]:
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        enable_idempotence=True,
    )
    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()
