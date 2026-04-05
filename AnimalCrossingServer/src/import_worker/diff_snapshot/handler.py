import uuid
from typing import Any, Awaitable, Callable, Tuple

from sqlalchemy import Select, exists, func, insert, literal, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import aliased

from import_worker.db.snapshot import (
    DiffChange,
    VillagerSnapshotActivation,
    VillagerSnapshotDiff,
    VillagerSnapshotDiffItems,
    VillagerSnapshotVillager,
)
from import_worker.dependencies import create_session
from messaging.imports.commands import CreateDiffWithActiveSnapshotCommand
from messaging.imports.events import DiffCreatedEvent


def create_diff_with_active_snapshot_handler(
    session_maker: async_sessionmaker[AsyncSession],
) -> Callable[
    ...,
    Awaitable[Any, Any, DiffCreatedEvent],
]:
    async def handle_wrapper(
        message: CreateDiffWithActiveSnapshotCommand,
    ) -> DiffCreatedEvent:
        async with create_session(session_maker) as session:
            return await handle(message, session)

    return handle_wrapper


async def handle(
    message: CreateDiffWithActiveSnapshotCommand,
    session: AsyncSession,
) -> DiffCreatedEvent:
    latest_activation = await session.scalar(
        select(VillagerSnapshotActivation)
        .order_by(VillagerSnapshotActivation.started_on.desc())
        .limit(1)
    )

    diff = VillagerSnapshotDiff.create(
        latest_activation.target if latest_activation is not None else None,
        message.snapshot_id,
    )
    session.add(diff)
    await session.flush()

    select_statements = [
        select_added_changes_from_snapshots(diff),
        select_updated_changes_from_snapshots(diff),
        select_deleted_changes_from_snapshots(diff),
    ]

    for select_statement in select_statements:
        insert_statement = insert(VillagerSnapshotDiffItems).from_select(
            ["diff_id", "villager_id", "change"], select_statement
        )
        await session.execute(insert_statement)

    await session.commit()

    amount_of_changes = await session.scalar(
        select(func.count(VillagerSnapshotDiffItems.diff_id)).where(
            VillagerSnapshotDiffItems.diff_id == diff.id
        )
    )

    return DiffCreatedEvent(
        saga_id=message.saga_id,
        diff_id=diff.id,
        differences_found=amount_of_changes > 0,
    )


def select_added_changes_from_snapshots(
    diff: VillagerSnapshotDiff,
) -> Select[Tuple[uuid.UUID, str, str]]:
    v1 = aliased(VillagerSnapshotVillager)
    v2 = aliased(VillagerSnapshotVillager)

    return (
        select(
            literal(diff.id),
            v1.id,
            literal(DiffChange.ADDED.name),
        )
        .where(v1.snapshot_id == diff.target)
        .where(
            ~exists(
                select(1).where(v1.id == v2.id).where(v2.snapshot_id == diff.source)
            )
        )
    )


def select_updated_changes_from_snapshots(
    diff: VillagerSnapshotDiff,
) -> Select[Tuple[uuid.UUID, str, str]]:
    v1 = aliased(VillagerSnapshotVillager)
    v2 = aliased(VillagerSnapshotVillager)

    return (
        select(
            literal(diff.id),
            v1.id,
            literal(DiffChange.UPDATED.name),
        )
        .where(v1.snapshot_id == diff.target)
        .where(
            exists(
                select(1)
                .where(v1.id == v2.id)
                .where(v1.checksum != v2.checksum)
                .where(v2.snapshot_id == diff.source)
            )
        )
    )


def select_deleted_changes_from_snapshots(
    diff: VillagerSnapshotDiff,
) -> Select[Tuple[uuid.UUID, str, str]]:
    v1 = aliased(VillagerSnapshotVillager)
    v2 = aliased(VillagerSnapshotVillager)

    return (
        select(
            literal(diff.id),
            v1.id,
            literal(DiffChange.DELETED.name),
        )
        .where(v1.snapshot_id == diff.source)
        .where(
            ~exists(
                select(1).where(v1.id == v2.id).where(v2.snapshot_id == diff.target)
            )
        )
    )
