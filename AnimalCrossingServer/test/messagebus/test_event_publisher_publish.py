import itertools

from aiokafka import AIOKafkaProducer, ConsumerRecord
from testcontainers.kafka import KafkaContainer

from api.db.villager import VillagerCreated
from api.messagebus.event_publisher import EventPublisher
from test.messagebus.kafka_consumer_context import kafka_consumer


async def test_should_publish_event_to_kafka(
    kafka_container: KafkaContainer, kafka_producer: AIOKafkaProducer
):
    # given
    publisher = EventPublisher(kafka_producer)

    # when
    await publisher.publish([VillagerCreated(id="flg01")])
    await kafka_producer.flush()

    # then
    async with kafka_consumer(kafka_container, topic="villagers") as consumer:
        messages = await consumer.getmany(timeout_ms=100)
        messagelist: list[ConsumerRecord] = list(itertools.chain(*messages.values()))
        assert messagelist[0].value == {"type": "VillagerCreated", "id": "flg01"}
