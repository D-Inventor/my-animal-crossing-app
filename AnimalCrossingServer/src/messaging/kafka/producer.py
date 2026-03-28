from aiokafka import AIOKafkaProducer

from messaging.config import KafkaSettings
from messaging.serialize import create_default_serializer


def create_producer() -> AIOKafkaProducer:
    kafka_settings = KafkaSettings()
    producer = AIOKafkaProducer(
        bootstrap_servers=kafka_settings.bootstrap_server,
        value_serializer=create_default_serializer().serialize,
        enable_idempotence=True,
    )
    return producer
