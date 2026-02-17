from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db.session import get_session
from api.db.villager import Villager

from .router import router


class GetVillagerByNameResponse(BaseModel):
    data: list[VillagerResponse]


class VillagerResponse(BaseModel):
    id: str
    name: str


@router.get("/by-name/{name}", summary="Find all villagers with the given name")
def endpoint(
    name: str, db: Annotated[Session, Depends(get_session)]
) -> GetVillagerByNameResponse:
    stmt = select(Villager).where(Villager.name == name)
    villagers = db.execute(stmt).scalars().all()
    return GetVillagerByNameResponse(
        data=[VillagerResponse(id=v.id, name=v.name) for v in villagers]
    )
