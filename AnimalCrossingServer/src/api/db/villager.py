from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Villager(Base):
    __tablename__ = "villagers"
    id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
