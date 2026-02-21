from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Villager(Base):
    __tablename__ = "villagers"
    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)

    def __eq__(self, other: Villager) -> bool:
        if not isinstance(other, Villager):
            return NotImplemented
        return self.id == other.id and self.name == other.name
