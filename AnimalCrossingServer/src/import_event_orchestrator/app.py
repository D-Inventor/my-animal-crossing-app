import asyncio
import logging

from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.config import DatabaseSettings
from import_event_orchestrator.db.saga_repository import SessionSagaRepository
from import_event_orchestrator.kafka_command_dispatcher import KafkaCommandDispatcher
from import_event_orchestrator.villager_import_orchestrator import (
    VillagerImportOrchestrator,
)
from messaging.consumer import create_consumer
from messaging.handler import bootstrap_signals
from messaging.producer import create_producer
from messaging.topics import MessageTopic

logger = logging.getLogger(__name__)


async def run_orchestrator() -> None:
    consumer = create_consumer(
        [MessageTopic.IMPORT_COMMANDS, MessageTopic.IMPORT_EVENTS],
        group_id="import-event-orchestrator",
    )
    producer = create_producer()
    engine = create_async_engine(DatabaseSettings().get_connection_url(), echo=False)
    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    await consumer.start()
    await producer.start()
    try:
        async for message in consumer:
            await process_message(producer, session_maker, message.value)
    finally:
        print("Shutting down orchestrator...")
        await consumer.stop()
        await producer.stop()
        await engine.dispose()


async def process_message(
    producer: AIOKafkaProducer,
    session_maker: async_sessionmaker[AsyncSession],
    message: object,
) -> None:
    try:
        async with session_maker() as session:
            repository = SessionSagaRepository(session)
            command_dispatcher = KafkaCommandDispatcher(producer)
            orchestrator = VillagerImportOrchestrator(repository, command_dispatcher)
            await orchestrator.handle(message)
            await session.commit()
    except Exception as e:
        logger.exception("Error processing message", exc_info=e)


async def execute() -> None:
    await bootstrap_signals(
        asyncio.get_running_loop(), asyncio.create_task(run_orchestrator())
    )
