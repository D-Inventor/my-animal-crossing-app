import logging
from contextlib import AsyncExitStack

from import_worker.dependencies import (
    create_engine,
    create_nookipedia_client,
)
from import_worker.diff_snapshot.handler import create_diff_with_active_snapshot_handler
from import_worker.download_snapshot.handler import (
    create_download_snapshot_handler,
)
from messaging import MessageTopic
from messaging.kafka import KafkaMessageHandlerApp

logger = logging.getLogger(__name__)


async def execute() -> None:
    async with AsyncExitStack() as stack:
        nookipedia_client = await stack.enter_async_context(create_nookipedia_client())
        session_maker = await stack.enter_async_context(create_engine())

        app = (
            KafkaMessageHandlerApp("import-worker")
            .add_topics([MessageTopic.IMPORT_COMMANDS])
            .add_handler_func(
                create_download_snapshot_handler(session_maker, nookipedia_client)
            )
            .add_handler_func(create_diff_with_active_snapshot_handler(session_maker))
        )

        await app.run()
