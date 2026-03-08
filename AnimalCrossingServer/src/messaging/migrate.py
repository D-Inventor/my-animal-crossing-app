import asyncio

from aiokafka.admin import AIOKafkaAdminClient, NewTopic

from messaging.config import KafkaSettings


async def install_topics(bootstrap_servers: str) -> None:
    client = AIOKafkaAdminClient(bootstrap_servers=bootstrap_servers)
    try:
        print(f"[messaging.migrate] Connecting to Kafka at {bootstrap_servers}...")
        await client.start()
        print(f"[messaging.migrate] Connected to Kafka at {bootstrap_servers}")

        await client.create_topics(
            new_topics=[
                NewTopic("villagers", num_partitions=1, replication_factor=1),
                NewTopic("import_events", num_partitions=1, replication_factor=1),
                NewTopic("import_commands", num_partitions=1, replication_factor=1),
            ]
        )
        print(
            "[messaging.migrate] Topics 'villagers' and 'import_events' created successfully"
        )
    finally:
        await client.close()
        print(f"[messaging.migrate] Closed connection to Kafka at {bootstrap_servers}")


def migrate_kafka() -> None:
    asyncio.run(install_topics(KafkaSettings().bootstrap_server))


def main() -> None:
    migrate_kafka()
