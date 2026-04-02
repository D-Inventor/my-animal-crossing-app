import uuid

from import_worker.db.snapshot import VillagerSpecies
from import_worker.download_snapshot.client import VillagersResponseItemData
from import_worker.download_snapshot.handler import map_to_entity


def test_should_create_entity_from_api_response():
    # given
    snapshot_id = uuid.uuid4()
    api_response_item = VillagersResponseItemData(
        id="gor16",
        name="Rocket",
        species="Gorilla",
        url="https://nookipedia.com/villagers/rocket",
    )

    # when
    result = map_to_entity(api_response_item, snapshot_id)

    # then
    assert result.id == "gor16"
    assert result.snapshot_id == snapshot_id
    assert result.name == "Rocket"
    assert result.url == "https://nookipedia.com/villagers/rocket"
    assert result.species == VillagerSpecies.GORILLA
    assert result.checksum == 631447837
