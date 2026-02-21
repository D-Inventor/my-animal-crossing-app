from typing import Annotated

from fastapi import Depends

from api.db.villager_repository import VillagerRepository, get_repository

from .router import router


@router.delete(
    "/{villager_id}", status_code=204, summary="Delete a villager with the given id"
)
async def endpoint(
    villager_id: str, repository: Annotated[VillagerRepository, Depends(get_repository)]
) -> None:
    villager = await repository.get(villager_id)
    if villager is None:
        return

    await repository.delete(villager)
    await repository.save()
