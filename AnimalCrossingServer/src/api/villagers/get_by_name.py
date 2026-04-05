from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.dependencies import get_session
from api.db.villager import Villager
from api_contract.villagers.get_by_name import (
    GetVillagerByNameResponse,
    VillagerResponse,
)

from .router import router


@router.get("/by-name/{name}", summary="Find all villagers with the given name")
async def endpoint(
    name: str, db: Annotated[AsyncSession, Depends(get_session)]
) -> GetVillagerByNameResponse:
    stmt = select(Villager).where(Villager.name == name)
    villagers = (await db.scalars(stmt)).all()
    return GetVillagerByNameResponse(
        data=[VillagerResponse(id=v.id, name=v.name) for v in villagers]
    )
