import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import pytest
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from import_worker.db.snapshot import (
    DiffChange,
    UtcDatetime,
    VillagerSnapshot,
    VillagerSnapshotActivation,
    VillagerSnapshotDiffItems,
    VillagerSnapshotVillager,
    VillagerSpecies,
)
from import_worker.diff_snapshot.handler import handle
from messaging.imports.commands import CreateDiffWithActiveSnapshotCommand

logging.basicConfig()
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


first_snapshot_date = UtcDatetime(datetime(2026, 4, 3, 12, 0, 0, tzinfo=timezone.utc))
second_snapshot_date = UtcDatetime(datetime(2026, 4, 4, 12, 0, 0, tzinfo=timezone.utc))
faker = Faker()


def create_villager(
    snapshot_id: uuid.UUID, **kwargs: dict[str, Any]
) -> VillagerSnapshotVillager:
    villager_data: dict[str, Any] = {
        "id": faker.random_element(["gor", "flg", "brc"])
        + str(faker.random_number(digits=2, fix_len=True)),
        "name": faker.name(),
        "url": faker.url(),
        "species": faker.enum(VillagerSpecies),
        "checksum": faker.random_number(),
    }

    villager_data = {**villager_data, **kwargs}

    return VillagerSnapshotVillager(snapshot_id=snapshot_id, **villager_data)


def create_snapshot_state():
    first_snapshot = VillagerSnapshot.create(first_snapshot_date)
    second_snapshot = VillagerSnapshot.create(second_snapshot_date)
    current_state = VillagerSnapshotActivation.create(
        None, first_snapshot.id, first_snapshot_date
    ).finish(first_snapshot_date)

    return first_snapshot, second_snapshot, current_state


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_diff_new_villager_as_added(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        first_snapshot, second_snapshot, current_state = create_snapshot_state()
        villager = create_villager(second_snapshot.id, id="gor16")
        session.add_all([first_snapshot, second_snapshot, villager, current_state])
        await session.commit()

    # when
    async with session_maker() as session:
        await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    async with session_maker() as session:
        diff = await session.scalar(select(VillagerSnapshotDiffItems))
        assert diff is not None
        assert diff.change == DiffChange.ADDED
        assert diff.villager_id == "gor16"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_diff_changed_villager_as_updated(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        first_snapshot, second_snapshot, current_state = create_snapshot_state()
        villager_before = create_villager(first_snapshot.id, id="gor16", checksum=22)
        villager_after = create_villager(second_snapshot.id, id="gor16", checksum=23)
        session.add_all(
            [
                first_snapshot,
                second_snapshot,
                villager_before,
                villager_after,
                current_state,
            ]
        )
        await session.commit()

    # when
    async with session_maker() as session:
        await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    async with session_maker() as session:
        diff = await session.scalar(select(VillagerSnapshotDiffItems))
        assert diff is not None
        assert diff.change == DiffChange.UPDATED
        assert diff.villager_id == "gor16"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_not_diff_unchanged_villager(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        first_snapshot, second_snapshot, current_state = create_snapshot_state()
        villager_before = create_villager(first_snapshot.id, id="gor16", checksum=22)
        villager_after = create_villager(second_snapshot.id, id="gor16", checksum=22)
        session.add_all(
            [
                first_snapshot,
                second_snapshot,
                villager_before,
                villager_after,
                current_state,
            ]
        )
        await session.commit()

    # when
    async with session_maker() as session:
        await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    async with session_maker() as session:
        diff = await session.scalar(select(VillagerSnapshotDiffItems))
        assert diff is None


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_diff_removed_villager_as_deleted(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        first_snapshot, second_snapshot, current_state = create_snapshot_state()
        villager = create_villager(first_snapshot.id, id="gor16")
        session.add_all(
            [
                first_snapshot,
                second_snapshot,
                villager,
                current_state,
            ]
        )
        await session.commit()

    # when
    async with session_maker() as session:
        await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    async with session_maker() as session:
        diff = await session.scalar(select(VillagerSnapshotDiffItems))
        assert diff is not None
        assert diff.change == DiffChange.DELETED
        assert diff.villager_id == "gor16"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_diff_also_without_current_state(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        _, second_snapshot, _ = create_snapshot_state()
        villager = create_villager(second_snapshot.id, id="gor16")
        session.add_all([second_snapshot, villager])
        await session.commit()

    # when
    async with session_maker() as session:
        await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    async with session_maker() as session:
        diff = await session.scalar(select(VillagerSnapshotDiffItems))
        assert diff is not None
        assert diff.change == DiffChange.ADDED
        assert diff.villager_id == "gor16"


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_return_diff_created_event(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        _, second_snapshot, _ = create_snapshot_state()
        villager = create_villager(second_snapshot.id, id="gor16")
        session.add_all([second_snapshot, villager])
        await session.commit()

    # when
    async with session_maker() as session:
        result = await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    assert result is not None
    assert result.differences_found


@pytest.mark.asyncio
@pytest.mark.slow
async def test_should_return_no_changes_when_nothing_has_changed(
    session_maker: async_sessionmaker[AsyncSession],
):
    # given
    async with session_maker() as session:
        first_snapshot, second_snapshot, current_state = create_snapshot_state()
        villager_before = create_villager(first_snapshot.id, id="gor16", checksum=22)
        villager_after = create_villager(second_snapshot.id, id="gor16", checksum=22)
        session.add_all(
            [
                first_snapshot,
                second_snapshot,
                villager_before,
                villager_after,
                current_state,
            ]
        )
        await session.commit()

    # when
    async with session_maker() as session:
        result = await handle(
            CreateDiffWithActiveSnapshotCommand(
                saga_id=uuid.uuid4(), snapshot_id=second_snapshot.id
            ),
            session,
        )

    # then
    assert result is not None
    assert not result.differences_found
