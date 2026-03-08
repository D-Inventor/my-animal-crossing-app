from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiokafka import AIOKafkaProducer

from messaging.producer import create_producer


@asynccontextmanager
async def kafka_lifespan_from_configuration() -> AsyncGenerator[AIOKafkaProducer]:

    producer = create_producer()

    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()
