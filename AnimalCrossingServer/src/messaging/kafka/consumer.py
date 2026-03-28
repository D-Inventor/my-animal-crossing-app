from aiokafka import AIOKafkaConsumer

from messaging.config import KafkaSettings
from messaging.serialize import create_default_serializer
from messaging.topics import MessageTopic


def create_consumer(topics: list[MessageTopic], group_id: str) -> AIOKafkaConsumer:
    kafka_settings = KafkaSettings()
    consumer = AIOKafkaConsumer(
        *[topic.value for topic in topics],
        bootstrap_servers=kafka_settings.bootstrap_server,
        group_id=group_id,
        value_deserializer=create_default_serializer().deserialize,
    )
    return consumer
