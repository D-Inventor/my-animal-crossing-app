import httpx
import pytest

from api_client.client import VillagerApiClient


@pytest.fixture()
def api_client(client: httpx.AsyncClient):
    return VillagerApiClient(client)
