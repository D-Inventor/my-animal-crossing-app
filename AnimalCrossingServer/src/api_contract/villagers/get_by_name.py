from pydantic import BaseModel


class GetVillagerByNameResponse(BaseModel):
    data: list[VillagerResponse]


class VillagerResponse(BaseModel):
    id: str
    name: str
