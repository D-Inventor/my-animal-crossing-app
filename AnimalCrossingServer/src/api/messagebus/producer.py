from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from pydantic_core import to_json

from api.messagebus.config import KafkaSettings


def set_kafka(app: FastAPI, producer: AIOKafkaProducer) -> None:
    app.state["_kafka_producer"] = producer


@asynccontextmanager
async def get_kafka_lifespan_from_config() -> AsyncGenerator[AIOKafkaProducer]:

    kafka_settings = KafkaSettings()
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_settings.bootstrap_server,
        value_serializer=lambda v: to_json(v),
        enable_idempotence=True,
    )

    try:
        await producer.start()
        yield producer
    finally:
        await producer.stop()
