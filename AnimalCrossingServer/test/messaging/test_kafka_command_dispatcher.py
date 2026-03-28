import itertools
from typing import AsyncGenerator
from uuid import uuid4

import pytest
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord
from pydantic_core import from_json
from testcontainers.kafka import KafkaContainer

from messaging.imports.commands import DownloadVillagerSnapshotCommand
from messaging.kafka.kafka_message_dispatcher import KafkaMessageDispatcher
from messaging.migrate import install_topics
from messaging.serialize import MessageSerialize
from messaging.topics import MessageTopic


@pytest.fixture
async def kafka_container() -> AsyncGenerator[KafkaContainer, None]:
    with KafkaContainer(image="confluentinc/cp-kafka:8.0.4").with_kraft() as kafka:
        await install_topics(kafka.get_bootstrap_server())
        yield kafka


@pytest.fixture
async def kafka_producer(
    kafka_container: KafkaContainer,
) -> AsyncGenerator[AIOKafkaProducer, None]:
    serializer = MessageSerialize()
    serializer.register_type(DownloadVillagerSnapshotCommand)
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_serializer=serializer.serialize,
        enable_idempotence=True,
    )
    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_dispatch_command_to_import_commands_topic(
    kafka_container: KafkaContainer,
    kafka_producer: AIOKafkaProducer,
) -> None:
    # given
    dispatcher = KafkaMessageDispatcher(kafka_producer)
    command = DownloadVillagerSnapshotCommand(saga_id=uuid4())

    # when
    await dispatcher.dispatch(command)
    await kafka_producer.flush()

    # then
    consumer = AIOKafkaConsumer(
        MessageTopic.IMPORT_COMMANDS.value,
        bootstrap_servers=kafka_container.get_bootstrap_server(),
        value_deserializer=lambda m: from_json(m),
        auto_offset_reset="earliest",
    )
    try:
        await consumer.start()
        messages = await consumer.getmany(timeout_ms=100)
        messagelist: list[ConsumerRecord] = list(itertools.chain(*messages.values()))
        assert len(messagelist) > 0
        assert messagelist[0].value["$type"] == "DownloadVillagerSnapshotCommand"
        assert messagelist[0].value["saga_id"] == str(command.saga_id)
    finally:
        await consumer.stop()
