from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Self
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, ForeignKey, String
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
        UtcDatetime(datetime=datetime.now(timezone.utc))

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
