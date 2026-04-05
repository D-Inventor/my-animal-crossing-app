from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
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
        return UtcDatetime(datetime=datetime.now(timezone.utc))

    def __add__(self, other: timedelta) -> UtcDatetime:
        return UtcDatetime(datetime=self.datetime + other)

    def __eq__(self, value: datetime) -> bool:
        return self.datetime == value


class VillagerSpecies(Enum):
    ALLIGATOR = "Alligator"
    ANTEATER = "Anteater"
    BEAR = "Bear"
    BEAR_CUB = "Bear cub"
    BIRD = "Bird"
    BULL = "Bull"
    CAT = "Cat"
    CHICKEN = "Chicken"
    COW = "Cow"
    DEER = "Deer"
    DOG = "Dog"
    DUCK = "Duck"
    EAGLE = "Eagle"
    ELEPHANT = "Elephant"
    FROG = "Frog"
    GOAT = "Goat"
    GORILLA = "Gorilla"
    HAMSTER = "Hamster"
    HIPPO = "Hippo"
    HORSE = "Horse"
    KANGAROO = "Kangaroo"
    KOALA = "Koala"
    LION = "Lion"
    MONKEY = "Monkey"
    MOUSE = "Mouse"
    OCTOPUS = "Octopus"
    OSTRICH = "Ostrich"
    PENGUIN = "Penguin"
    PIG = "Pig"
    RABBIT = "Rabbit"
    RHINOCEROS = "Rhinoceros"
    SHEEP = "Sheep"
    SQUIRREL = "Squirrel"
    TIGER = "Tiger"
    WOLF = "Wolf"


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
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    species: Mapped[VillagerSpecies] = mapped_column(
        SQLEnum(VillagerSpecies), nullable=False
    )
    checksum: Mapped[int] = mapped_column(BigInteger(), nullable=False)


class DiffChange(Enum):
    ADDED = "added"
    UPDATED = "updated"
    DELETED = "deleted"


class VillagerSnapshotDiff(Base):
    __tablename__ = "villager_snapshot_diff"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    source: Mapped[UUID] = mapped_column(
        ForeignKey("villager_snapshots.id"), nullable=True
    )
    target: Mapped[UUID] = mapped_column(ForeignKey("villager_snapshots.id"))
    __table_args__ = (UniqueConstraint("source", "target"),)

    @classmethod
    def create(cls, source: UUID | None, target: UUID) -> Self:
        return VillagerSnapshotDiff(id=uuid4(), source=source, target=target)


class VillagerSnapshotDiffItems(Base):
    __tablename__ = "villager_snapshot_diff_items"
    diff_id: Mapped[UUID] = mapped_column(
        ForeignKey("villager_snapshot_diff.id"), primary_key=True
    )
    villager_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    change: Mapped[DiffChange] = mapped_column(SQLEnum(DiffChange), nullable=False)


class VillagerSnapshotActivation(Base):
    __tablename__ = "villager_snapshot_activations"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    source: Mapped[UUID] = mapped_column(
        ForeignKey("villager_snapshots.id"), nullable=True
    )
    target: Mapped[UUID] = mapped_column(ForeignKey("villager_snapshots.id"))
    started_on: Mapped[datetime] = mapped_column(nullable=False)
    finished_on: Mapped[datetime] = mapped_column(nullable=True)

    @classmethod
    def create(
        cls, source: UUID | None, target: UUID, now: UtcDatetime
    ) -> VillagerSnapshotActivation:
        return cls(id=uuid4(), source=source, target=target, started_on=now.datetime)

    def finish(self, now: UtcDatetime) -> VillagerSnapshotActivation:
        self.finished_on = now.datetime
        return self
