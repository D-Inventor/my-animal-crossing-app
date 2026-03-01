from aiokafka.admin import AIOKafkaAdminClient, NewTopic


async def install_topics(bootstrap_servers: str) -> None:
    client = AIOKafkaAdminClient(bootstrap_servers=bootstrap_servers)
    try:
        await client.start()

        await client.create_topics(
            new_topics=[NewTopic("villagers", num_partitions=1, replication_factor=1)]
        )
    finally:
        await client.close()
