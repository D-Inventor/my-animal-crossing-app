import logging
from contextlib import AsyncExitStack
from types import CoroutineType
from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from import_event_orchestrator.db.saga_repository import SessionSagaRepository
from import_event_orchestrator.dependencies import (
    create_engine,
    create_session,
)
from import_event_orchestrator.villager_import_orchestrator import (
    VillagerImportOrchestrator,
)
from messaging import MessageTopic
from messaging.handler import (
    MessageContext,
    accept_all_messages,
)
from messaging.kafka import KafkaMessageHandlerApp

logger = logging.getLogger(__name__)


async def execute() -> None:
    async with AsyncExitStack() as stack:
        session_maker = await stack.enter_async_context(create_engine())

        app = (
            KafkaMessageHandlerApp("import-event-orchestrator")
            .add_topics(
                [MessageTopic.IMPORT_ORCHESTRATOR_COMMANDS, MessageTopic.IMPORT_EVENTS]
            )
            .add_handler_func(
                create_message_processor(session_maker), accept_all_messages
            )
        )

        await app.run()


def create_message_processor(
    session_maker: async_sessionmaker[AsyncSession],
) -> Callable[..., CoroutineType[Any, Any, None]]:
    async def message_processor(message: object, context: MessageContext) -> None:
        async with create_session(session_maker) as session:
            repository = SessionSagaRepository(session)
            await process_message(message, context, session, repository)

    return message_processor


async def process_message(
    message: object,
    context: MessageContext,
    session: AsyncSession,
    repository: SessionSagaRepository,
) -> None:
    try:
        orchestrator = VillagerImportOrchestrator(repository)
        await orchestrator.handle(message, context)
        await session.commit()
    except Exception as e:
        logger.exception("Error processing message", exc_info=e)
