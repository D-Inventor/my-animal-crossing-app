import itertools
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import pytest
from aiokafka import AIOKafkaProducer, ConsumerRecord
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine
from testcontainers.kafka import KafkaContainer

from api.app_builder import AppBuilder
from messaging.kafka import KafkaMessageDispatcher
from test.api.messagebus.kafka_consumer_context import kafka_consumer


@pytest.mark.asyncio
@pytest.mark.slow
async def test_event_published_to_kafka_on_request(
    kafka_container: KafkaContainer,
    kafka_producer: AIOKafkaProducer,
    mariadb_reset_engine: AsyncEngine,
):
    # given
    @asynccontextmanager
    async def producer_manager() -> AsyncGenerator[AIOKafkaProducer]:
        yield KafkaMessageDispatcher(kafka_producer)

    app = (
        AppBuilder()
        .add_database_engine(lambda: mariadb_reset_engine)
        .add_message_publisher(producer_manager)
        .build()
    )

    # when
    async with LifespanManager(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            await client.put("/villagers/flg01", json={"name": "Ribbot"})
        await kafka_producer.flush()

    # then
    async with kafka_consumer(kafka_container, "villagers") as consumer:
        messages = await consumer.getmany(timeout_ms=100)
        messagelist: list[ConsumerRecord] = list(itertools.chain(*messages.values()))
        assert len(messagelist) > 0
        assert messagelist[0].value == {"$type": "VillagerCreated", "id": "flg01"}
