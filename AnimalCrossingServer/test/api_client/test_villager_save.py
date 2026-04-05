import pytest

from api_client import VillagerApiClient
from api_contract.villagers.save import SaveVillagerRequest
from test.api_mock import ApiMock, HttpMethod


@pytest.mark.asyncio
async def test_should_send_request_to_api(api: ApiMock, api_client: VillagerApiClient):
    # given
    api.for_request(HttpMethod.POST, "/villagers/gor16").respond_with(status_code=200)

    # when
    await api_client.save("gor16", SaveVillagerRequest(name="Rocket"))

    # then
    request = api.for_request(HttpMethod.POST, "/villagers/gor16").get_last_request()
    assert request is not None
    assert request.payload == {"name": "Rocket"}


@pytest.mark.asyncio
async def test_should_raise_exception_when_response_is_not_success(
    api: ApiMock, api_client: VillagerApiClient
):
    # given
    api.for_request(HttpMethod.POST, "/villagers/gor16").respond_with(status_code=500)

    # when / then
    with pytest.raises(ValueError):
        await api_client.save("gor16", SaveVillagerRequest(name="Rocket"))
