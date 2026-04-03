import logging
import zlib
from typing import Callable
from uuid import UUID

from pydantic_core import to_json
from sqlalchemy.ext.asyncio import AsyncSession

from import_worker.db.snapshot import (
    UtcDatetime,
    VillagerSnapshot,
    VillagerSnapshotVillager,
    VillagerSpecies,
)
from import_worker.download_snapshot.client import (
    VillagersAPIProtocol,
    VillagersRequest,
    VillagersResponseItemData,
)
from messaging.imports.commands import DownloadVillagerSnapshotCommand
from messaging.imports.events import (
    VillagerSnapshotDownloadedEvent,
    VillagerSnapshotDownloadFailedEvent,
)

logger = logging.getLogger(__name__)


async def handle(
    message: DownloadVillagerSnapshotCommand,
    clock: Callable[[], UtcDatetime],
    session: AsyncSession,
    villager_api: VillagersAPIProtocol,
) -> VillagerSnapshotDownloadedEvent | VillagerSnapshotDownloadFailedEvent:
    try:
        snapshot = VillagerSnapshot.create(clock())
        session.add(snapshot)
        await session.flush()

        # Downloading is funny: we don't know how many villagers
        #   exist until we've fetched them all
        offset = 0
        limit = 100
        while True:
            response = await villager_api.get_villagers(
                VillagersRequest(limit=limit, offset=offset)
            )

            villagers = [
                map_to_entity(item.title, snapshot.id) for item in response.cargoquery
            ]
            session.add_all(villagers)
            await session.flush()
            session.expunge_all()

            if len(response.cargoquery) < limit:
                break
            else:
                offset += limit

        snapshot = await session.get(VillagerSnapshot, snapshot.id)
        snapshot.finish(clock())
        await session.commit()

        return VillagerSnapshotDownloadedEvent(
            saga_id=message.saga_id, snapshot_id=snapshot.id
        )
    except Exception as e:
        logger.error("failed to download snapshot", exc_info=e)
        return VillagerSnapshotDownloadFailedEvent(saga_id=message.saga_id)


def map_to_entity(
    api_villager: VillagersResponseItemData, snapshot_id: UUID
) -> VillagerSnapshotVillager:
    result = VillagerSnapshotVillager(
        id=api_villager.id,
        snapshot_id=snapshot_id,
        name=api_villager.name,
        url=api_villager.url,
        species=VillagerSpecies(api_villager.species),
    )

    checksum_obj = {
        "id": result.id,
        "name": result.name,
        "url": result.url,
        "species": result.species,
    }

    result.checksum = zlib.adler32(to_json(checksum_obj))

    return result
