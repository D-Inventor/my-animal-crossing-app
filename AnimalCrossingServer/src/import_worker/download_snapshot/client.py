from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from pydantic import BaseModel
from pydantic_core import from_json


class VillagersResponse(BaseModel):
    cargoquery: list[VillagersResponseItem]


class VillagersResponseItem(BaseModel):
    title: VillagersResponseItemData


class VillagersResponseItemData(BaseModel):
    id: str
    name: str
    species: str
    url: str


@dataclass(frozen=True)
class VillagersRequest:
    limit: int
    offset: int


class VillagersAPIProtocol(Protocol):
    async def get_villagers(self, request: VillagersRequest) -> VillagersResponse: ...


class NookipediaClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def get_villagers(self, request: VillagersRequest) -> VillagersResponse:

        params: dict[str, Any] = {}
        params["action"] = "cargoquery"
        params["format"] = "json"
        params["tables"] = "nh_villager,villager"
        params["join_on"] = "villager.url=nh_villager.url"
        params["fields"] = (
            "nh_villager.name,nh_villager.species,nh_villager.url,villager.id"
        )
        params["order_by"] = "villager.id"
        params["limit"] = request.limit
        params["offset"] = request.offset
        response = await self._client.get("/w/api.php", params=params)

        return VillagersResponse.model_validate(from_json(response.content))
