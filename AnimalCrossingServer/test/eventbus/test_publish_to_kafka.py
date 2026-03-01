import json
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from testcontainers.kafka import KafkaContainer


@asynccontextmanager
async def kafka_consumer(
    kafka_container: KafkaContainer, topic: str
) -> AsyncGenerator[AIOKafkaConsumer, None]:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        group_id="test-group",
    )
    try:
        await consumer.start()
        yield consumer
    finally:
        await consumer.stop()


@pytest.mark.asyncio
async def test_should_send_events_to_kafka(
    kafka_container: KafkaContainer, kafka_producer: AIOKafkaProducer
):
    # given
    kafka_host = kafka_container.get_bootstrap_server()
    topic = "test-topic"

    admin = AIOKafkaAdminClient(bootstrap_servers=kafka_host)
    await admin.start()
    try:
        await admin.create_topics(
            [NewTopic(name=topic, num_partitions=1, replication_factor=1)]
        )
    finally:
        await admin.close()

    # when
    test_message = {"event": "villager_created", "villager_id": "123"}
    await kafka_producer.send_and_wait(topic, value=test_message)

    # Create consumer and read message
    async with kafka_consumer(kafka_container, topic) as consumer:
        message = await consumer.getone()
        assert message.value == test_message
