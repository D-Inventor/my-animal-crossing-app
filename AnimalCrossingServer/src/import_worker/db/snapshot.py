from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


@dataclass(frozen=True)
class UtcDatetime:
    datetime: datetime

    def __post_init__(self) -> None:
        if self.datetime.tzinfo != timezone.utc:
            raise ValueError("utcnow is not a utc datetime")

    @classmethod
    def now(cls) -> UtcDatetime:
        UtcDatetime(datetime=datetime.now(timezone.utc))

    def __add__(self, other: timedelta) -> UtcDatetime:
        return UtcDatetime(datetime=self.datetime + other)

    def __eq__(self, value: datetime) -> bool:
        return self.datetime == value


class VillagerSnapshot(Base):
    __tablename__ = "villager_snapshots"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    started_on: Mapped[datetime] = mapped_column(nullable=False)
    finished_on: Mapped[datetime | None] = mapped_column(nullable=True)

    @classmethod
    def create(cls, utcnow: UtcDatetime) -> Self:
        return VillagerSnapshot(id=uuid4(), started_on=utcnow.datetime)

    def finish(self, utcnow: UtcDatetime) -> None:
        self.finished_on = utcnow.datetime


class VillagerSnapshotVillager(Base):
    __tablename__ = "villager_snapshot_villagers"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[UUID] = mapped_column(
        ForeignKey("villager_snapshots.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[int] = mapped_column(nullable=False)
