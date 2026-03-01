from dataclasses import dataclass
from typing import Self, TypedDict, Unpack

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VillagerType(TypedDict):
    id: str
    name: str


@dataclass
class VillagerCreated:
    id: str


class Villager(Base):
    __tablename__ = "villagers"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    _events: list[VillagerCreated] = []

    @classmethod
    def create(cls, **kwargs: Unpack[VillagerType]) -> Self:
        result = Villager(**kwargs)
        result._events.append(VillagerCreated(result.id))
        return result

    # Note: maybe overkill for now, but a list is easier to deal with
    #   and we might find need for other events later anyway
    def consume_events(self) -> list[VillagerCreated]:
        result = self._events
        self._events = []
        return result

    def __eq__(self, other: Villager) -> bool:
        if not isinstance(other, Villager):
            return NotImplemented
        return self.id == other.id and self.name == other.name
