import asyncio
import signal

from messaging.consumer import create_consumer
from messaging.topics import MessageTopic


async def run_orchestrator() -> None:
    consumer = create_consumer(
        [MessageTopic.IMPORT_EVENTS], group_id="import-event-orchestrator"
    )

    await consumer.start()
    try:
        async for message in consumer:
            print(f"Received message: {message.value}")
    finally:
        print("Shutting down orchestrator...")
        await consumer.stop()


async def execute() -> None:
    main_task = asyncio.create_task(run_orchestrator())

    def signal_handler(sig: int) -> None:
        print(f"Received signal {sig}, shutting down...")
        main_task.cancel()

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler, signal.SIGINT)
    loop.add_signal_handler(signal.SIGTERM, signal_handler, signal.SIGTERM)

    try:
        await main_task
    except asyncio.CancelledError:
        print("Orchestrator task cancelled, exiting...")
