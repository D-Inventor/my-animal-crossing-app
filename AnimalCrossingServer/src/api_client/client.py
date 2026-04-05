from string import Template
from string.templatelib import Interpolation
from urllib.parse import quote

import httpx

from api_contract.villagers.save import SaveVillagerRequest


class VillagerApiClient:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def save(self, id: str, data: SaveVillagerRequest) -> None:
        url_template = t"/villagers/{id}"
        url = url_encode(url_template)
        response = await self._client.post(url, content=data.model_dump_json())
        if not response.is_success:
            raise ValueError("Response indicated failure")

    async def delete(self, id: str) -> None:
        url_template = t"/villagers/{id}"
        url = url_encode(url_template)
        response = await self._client.delete(url)
        if not response.is_success:
            raise ValueError("Response indicated failure")


def url_encode(url_template: Template) -> str:
    output = []
    for segment in url_template:
        if isinstance(segment, Interpolation):
            output.append(quote(str(segment.value)))
        else:
            output.append(segment)

    return "".join(output)
