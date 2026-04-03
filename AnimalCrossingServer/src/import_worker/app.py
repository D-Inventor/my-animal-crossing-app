import logging
import uuid
from contextlib import AsyncExitStack
from typing import Any, Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from import_worker.db.snapshot import UtcDatetime
from import_worker.dependencies import (
    create_engine,
    create_nookipedia_client,
    create_session,
)
from import_worker.download_snapshot.client import NookipediaClient
from import_worker.download_snapshot.handler import handle
from messaging import MessageTopic
from messaging.imports.commands import DownloadVillagerSnapshotCommand
from messaging.imports.events import (
    VillagerSnapshotDownloadedEvent,
    VillagerSnapshotDownloadFailedEvent,
)
from messaging.kafka import KafkaMessageHandlerApp

logger = logging.getLogger(__name__)


async def execute() -> None:
    async with AsyncExitStack() as stack:
        nookipedia_client = await stack.enter_async_context(create_nookipedia_client())
        session_maker = await stack.enter_async_context(create_engine())

        app = (
            KafkaMessageHandlerApp("import-worker")
            .add_topics([MessageTopic.IMPORT_COMMANDS])
            .add_handler_func(create_handle_func(session_maker, nookipedia_client))
        )

        await app.run()


def create_handle_func(
    session_maker: async_sessionmaker[AsyncSession], nookipedia_client: NookipediaClient
) -> Callable[
    ...,
    Awaitable[
        Any, Any, VillagerSnapshotDownloadedEvent | VillagerSnapshotDownloadFailedEvent
    ],
]:
    async def handle_wrapper(
        message: DownloadVillagerSnapshotCommand,
    ) -> VillagerSnapshotDownloadedEvent | VillagerSnapshotDownloadFailedEvent:
        async with create_session(session_maker) as session:
            return await handle(message, UtcDatetime.now, session, nookipedia_client)

    return handle_wrapper


def process_message(
    message: DownloadVillagerSnapshotCommand,
) -> VillagerSnapshotDownloadedEvent:
    logger.debug("received: %s", message)
    return VillagerSnapshotDownloadedEvent(
        saga_id=message.saga_id, snapshot_id=uuid.uuid4()
    )
