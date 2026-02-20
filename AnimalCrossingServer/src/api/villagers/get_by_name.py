from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.session import get_session
from api.db.villager import Villager

from .router import router


class GetVillagerByNameResponse(BaseModel):
    data: list[VillagerResponse]


class VillagerResponse(BaseModel):
    id: str
    name: str


@router.get("/by-name/{name}", summary="Find all villagers with the given name")
async def endpoint(
    name: str, db: Annotated[AsyncSession, Depends(get_session)]
) -> GetVillagerByNameResponse:
    stmt = select(Villager).where(Villager.name == name)
    villagers = (await db.scalars(stmt)).all()
    return GetVillagerByNameResponse(
        data=[VillagerResponse(id=v.id, name=v.name) for v in villagers]
    )
