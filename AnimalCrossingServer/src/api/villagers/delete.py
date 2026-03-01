from typing import Annotated

from fastapi import Depends

from api.db.unit_of_work import UnitOfWork, get_unit_of_work
from api.db.villager_repository import VillagerRepository, get_repository

from .router import router


@router.delete(
    "/{villager_id}", status_code=204, summary="Delete a villager with the given id"
)
async def endpoint(
    villager_id: str,
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    repository: Annotated[VillagerRepository, Depends(get_repository)],
) -> None:
    villager = await repository.get(villager_id)
    if villager is None:
        return

    await repository.delete(villager)
    await unit_of_work.save()
