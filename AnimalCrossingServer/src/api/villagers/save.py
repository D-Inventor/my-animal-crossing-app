from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel

from api.db.villager import Villager
from api.db.villager_repository import VillagerRepository, get_repository

from .router import router


class SaveVillagerRequest(BaseModel):
    name: str


@router.put("/{villager_id}", summary="Save a villager with the given id")
async def endpoint(
    villager_id: str,
    request: SaveVillagerRequest,
    repository: Annotated[VillagerRepository, Depends(get_repository)],
) -> None:
    villager = await repository.get(villager_id)
    villager = (
        create(villager_id, request) if villager is None else update(villager, request)
    )
    await repository.update(villager)
    await repository.save()


def create(id: str, request: SaveVillagerRequest) -> Villager:
    return Villager.create(id=id, name=request.name)


def update(villager: Villager, request: SaveVillagerRequest) -> Villager:
    villager.name = request.name
    return villager
