import httpx
import pytest

from import_worker.download_snapshot.client import NookipediaClient, VillagersRequest

from .conftest import ApiMock, HttpMethod

default_json_response = {
    "cargoquery": [
        {
            "title": {
                "name": "Ace",
                "species": "Bird",
                "url": "https://nookipedia.com/wiki/Ace",
                "id": "brd09",
            }
        }
    ]
}


@pytest.mark.asyncio
async def test_should_get_data_with_expected_query_parameters(
    api: ApiMock, client: httpx.AsyncClient
) -> None:
    # given
    api.for_request(HttpMethod.GET, "/w/api.php").respond_with(
        status_code=200,
        json=default_json_response,
    )
    nookipedia_client = NookipediaClient(client)

    # when
    await nookipedia_client.get_villagers(VillagersRequest(limit=100, offset=10))

    # then
    request = api.for_request(HttpMethod.GET, "/w/api.php").get_last_request()
    assert request is not None
    assert request.params.get("limit") == "100"
    assert request.params.get("offset") == "10"
    assert request.params.get("action") == "cargoquery"
    assert request.params.get("format") == "json"
    assert request.params.get("tables") == "nh_villager,villager"
    assert request.params.get("join_on") == "villager.url=nh_villager.url"
    assert (
        request.params.get("fields")
        == "nh_villager.name,nh_villager.species,nh_villager.url,villager.id"
    )
    assert request.params.get("order_by") == "villager.id"


@pytest.mark.asyncio
async def test_should_parse_response_from_json(
    api: ApiMock, client: httpx.AsyncClient
) -> None:
    # given
    api.for_request(HttpMethod.GET, "/w/api.php").respond_with(
        status_code=200,
        json=default_json_response,
    )
    nookipedia_client = NookipediaClient(client)

    # when
    response = await nookipedia_client.get_villagers(
        VillagersRequest(limit=1, offset=0)
    )

    # then
    assert len(response.cargoquery) == 1
    assert response.cargoquery[0].title.id == "brd09"
    assert response.cargoquery[0].title.species == "Bird"
    assert response.cargoquery[0].title.url == "https://nookipedia.com/wiki/Ace"
    assert response.cargoquery[0].title.name == "Ace"
