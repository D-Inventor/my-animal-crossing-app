import itertools

import pytest
from aiokafka import AIOKafkaProducer, ConsumerRecord
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from testcontainers.kafka import KafkaContainer

from api.app import create_app
from api.messagebus.config import configure_messagebus
from test.messagebus.kafka_consumer_context import kafka_consumer


@pytest.mark.asyncio
@pytest.mark.slow
async def test_event_published_to_kafka_on_request(
    kafka_container: KafkaContainer,
    kafka_producer: AIOKafkaProducer,
    mariadb_session: async_sessionmaker[AsyncSession],
):
    # given
    app = create_app()
    app.state._session_local = mariadb_session
    app.state._kafka_producer = kafka_producer
    configure_messagebus(app)

    # when
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
        assert messagelist[0].value == {"type": "VillagerCreated", "id": "flg01"}
