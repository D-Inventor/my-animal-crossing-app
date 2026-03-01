from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from pydantic import Field
from pydantic_core import to_json
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.db.event_handler import get_event_handler_collection_from_app
from api.messagebus.event_publisher import EventPublisher


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    bootstrap_server: str = Field()


def get_kafka_producer_from_app(app: FastAPI) -> AIOKafkaProducer:
    key = "_kafka_producer"
    if not hasattr(app.state, key):
        kafka_settings = KafkaSettings()
        app.state[key] = AIOKafkaProducer(
            bootstrap_servers=kafka_settings.bootstrap_server,
            value_serializer=lambda v: to_json(v),
            enable_idempotence=True,
        )

    return app.state[key]


def configure_messagebus(app: FastAPI) -> None:
    producer = get_kafka_producer_from_app(app)
    event_handler = get_event_handler_collection_from_app(app)
    publisher = EventPublisher(producer)
    event_handler.subscribe(publisher.publish)
