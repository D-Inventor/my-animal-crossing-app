import pytest

from api_client import VillagerApiClient
from test.api_mock import ApiMock, HttpMethod


@pytest.mark.asyncio
async def test_should_send_delete_request(api: ApiMock, api_client: VillagerApiClient):
    # given
    api.for_request(HttpMethod.DELETE, "/villagers/gor16").respond_with(status_code=200)

    # when
    await api_client.delete("gor16")

    # then
    request = api.for_request(HttpMethod.DELETE, "/villagers/gor16").get_last_request()
    assert request is not None
    assert request.payload is None


@pytest.mark.asyncio
async def test_should_raise_exception_when_response_is_not_success(
    api: ApiMock, api_client: VillagerApiClient
):
    # given
    api.for_request(HttpMethod.DELETE, "/villagers/gor16").respond_with(status_code=500)

    # when / then
    with pytest.raises(ValueError):
        await api_client.delete("gor16")
