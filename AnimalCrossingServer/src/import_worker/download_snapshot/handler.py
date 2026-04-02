import zlib
from typing import Callable
from uuid import UUID

from pydantic_core import to_json
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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
from messaging.imports.events import VillagerSnapshotDownloadedEvent


async def handle(
    message: DownloadVillagerSnapshotCommand,
    clock: Callable[[], UtcDatetime],
    session_maker: async_sessionmaker[AsyncSession],
    villager_api: VillagersAPIProtocol,
) -> VillagerSnapshotDownloadedEvent:
    async with session_maker() as session:
        snapshot = VillagerSnapshot.create(clock())
        session.add(snapshot)
        await session.commit()

    # Downloading is funny: we don't know how many villagers
    #   exist until we've fetched them all
    offset = 0
    limit = 100
    while True:
        response = await villager_api.get_villagers(
            VillagersRequest(limit=limit, offset=offset)
        )

        async with session_maker() as session:
            villagers = [
                map_to_entity(item.title, snapshot.id) for item in response.cargoquery
            ]
            session.add_all(villagers)
            await session.commit()

        if len(response.cargoquery) < limit:
            break
        else:
            offset += limit

    async with session_maker() as session:
        snapshot = await session.get(VillagerSnapshot, snapshot.id)
        snapshot.finish(clock())
        await session.commit()

    return VillagerSnapshotDownloadedEvent(
        saga_id=message.saga_id, snapshot_id=snapshot.id
    )


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
