from typing import AsyncGenerator
from uuid import uuid4

import pytest
from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from testcontainers.kafka import KafkaContainer

from import_event_orchestrator.app import process_message
from import_event_orchestrator.db.saga_state import SagaState
from messaging.imports.commands import ImportVillagersCommand
from messaging.migrate import install_topics
from messaging.serialize import create_default_serializer


@pytest.fixture
async def kafka_container() -> AsyncGenerator[KafkaContainer, None]:
    with KafkaContainer(image="confluentinc/cp-kafka:8.0.4").with_kraft() as kafka:
        await install_topics(kafka.get_bootstrap_server())
        yield kafka


@pytest.fixture
async def kafka_command_producer(
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


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_persist_saga_when_import_command_received(
    kafka_command_producer: AIOKafkaProducer,
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    # given
    command_id = uuid4()
    command = ImportVillagersCommand(id=command_id)

    # when
    await process_message(kafka_command_producer, session_maker, command)
    await kafka_command_producer.flush()

    # then
    async with session_maker() as then_session:
        saga = await then_session.get(SagaState, command_id)
        assert saga is not None
