import logging
import uuid

from messaging import MessageTopic
from messaging.imports.commands import DownloadVillagerSnapshotCommand
from messaging.imports.events import VillagerSnapshotDownloadedEvent
from messaging.kafka import KafkaMessageHandlerApp

logger = logging.getLogger(__name__)


async def execute() -> None:
    app = (
        KafkaMessageHandlerApp("import-worker")
        .add_topics([MessageTopic.IMPORT_COMMANDS])
        .add_handler_func(process_message)
    )

    await app.run()


def process_message(
    message: DownloadVillagerSnapshotCommand,
) -> VillagerSnapshotDownloadedEvent:
    logger.debug("received: %s", message)
    return VillagerSnapshotDownloadedEvent(
        saga_id=message.saga_id, snapshot_id=uuid.uuid4()
    )
