import uuid
from datetime import datetime, timezone

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from import_worker.db.snapshot import (
    Base,
    UtcDatetime,
    VillagerSnapshot,
    VillagerSnapshotVillager,
    VillagerSpecies,
)
from import_worker.download_snapshot.client import (
    VillagersRequest,
    VillagersResponse,
    VillagersResponseItem,
    VillagersResponseItemData,
)
from import_worker.download_snapshot.handler import handle
from messaging.imports.commands import DownloadVillagerSnapshotCommand
from messaging.imports.events import (
    VillagerSnapshotDownloadFailedEvent,
)


def clock():
    return UtcDatetime(datetime=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc))


def generate_villager(faker: Faker) -> VillagersResponseItem:
    return VillagersResponseItem(
        title=VillagersResponseItemData(
            id=str(uuid.uuid4()),
            name=faker.name(),
            species=faker.enum(VillagerSpecies).value,
            url=faker.url(["https"]),
        )
    )


class FakeVillagerAPI:
    def __init__(self, amount: int = 1):
        faker = Faker()
        self._response_villagers = [generate_villager(faker) for x in range(amount)]

    async def get_villagers(self, request: VillagersRequest) -> VillagersResponse:
        return VillagersResponse(
            cargoquery=self._response_villagers[
                request.offset : (request.offset + request.limit)
            ]
        )


class FailureVillagerAPIStub:
    async def get_villagers(self, request: VillagersRequest) -> VillagersResponse:
        raise ValueError("Something went wrong")


@pytest.mark.asyncio
async def test_should_create_snapshot(session_maker):
    # given
    command = DownloadVillagerSnapshotCommand(saga_id=uuid.uuid4())

    # when
    async with session_maker() as session:
        result = await handle(command, clock, session, FakeVillagerAPI())

    # then
    async with session_maker() as session:
        snapshot = await session.get(VillagerSnapshot, result.snapshot_id)
        assert snapshot is not None
        assert snapshot.finished_on is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("amount", [10, 101, 201])
async def test_should_fetch_all_villagers(session_maker, amount):
    # given
    command = DownloadVillagerSnapshotCommand(saga_id=uuid.uuid4())
    api = FakeVillagerAPI(amount)

    # when
    async with session_maker() as session:
        result = await handle(command, clock, session, api)

    # then
    async with session_maker() as session:
        snapshot_villagers = (
            (
                await session.execute(
                    select(VillagerSnapshotVillager).where(
                        VillagerSnapshotVillager.snapshot_id == result.snapshot_id
                    )
                )
            )
            .scalars()
            .all()
        )

        assert len(snapshot_villagers) == amount


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_return_failure_when_api_fails_to_fetch(session_maker):
    # given
    command = DownloadVillagerSnapshotCommand(saga_id=uuid.uuid4())
    api = FailureVillagerAPIStub()

    # when
    async with session_maker() as session:
        result = await handle(command, clock, session, api)

    # then
    assert isinstance(result, VillagerSnapshotDownloadFailedEvent)
    assert result.saga_id == command.saga_id
