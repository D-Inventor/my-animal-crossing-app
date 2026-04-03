import asyncio

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from .config import KafkaSettings
from .topics import MessageTopic


async def install_topics(bootstrap_servers: str) -> None:
    client = AIOKafkaAdminClient(bootstrap_servers=bootstrap_servers)
    try:
        print(f"[messaging.migrate] Connecting to Kafka at {bootstrap_servers}...")
        await client.start()
        print(f"[messaging.migrate] Connected to Kafka at {bootstrap_servers}")

        await client.create_topics(
            new_topics=[
                NewTopic(
                    MessageTopic.VILLAGERS, num_partitions=1, replication_factor=1
                ),
                NewTopic(
                    MessageTopic.IMPORT_EVENTS, num_partitions=1, replication_factor=1
                ),
                NewTopic(
                    MessageTopic.IMPORT_COMMANDS, num_partitions=1, replication_factor=1
                ),
                NewTopic(
                    MessageTopic.IMPORT_ORCHESTRATOR_COMMANDS,
                    num_partitions=1,
                    replication_factor=1,
                ),
            ]
        )
        print("[messaging.migrate] Topics created successfully")
    finally:
        await client.close()
        print(f"[messaging.migrate] Closed connection to Kafka at {bootstrap_servers}")


def migrate_kafka() -> None:
    asyncio.run(install_topics(KafkaSettings().bootstrap_server))


def main() -> None:
    migrate_kafka()
