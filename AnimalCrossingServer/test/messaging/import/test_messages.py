import uuid

import pytest

from messaging import default_serializer
from messaging.imports.commands import (
    DownloadVillagerSnapshotCommand,
    ImportVillagersCommand,
)
from messaging.imports.events import VillagerSnapshotDownloadedEvent


@pytest.mark.parametrize(
    "msg",
    [
        ImportVillagersCommand(id=uuid.UUID("{b7aef3cd-99d3-4d16-b2ae-3ab4a66a0705}")),
        DownloadVillagerSnapshotCommand(
            saga_id=uuid.UUID("{e7506b2b-75a6-4e38-9264-9985e6564e45}")
        ),
        VillagerSnapshotDownloadedEvent(
            saga_id=uuid.UUID("{988f44d7-9f34-4dac-864e-49b5f390c7c2}"),
            snapshot_id=uuid.UUID("{86c78338-2a48-4014-9355-2d1855500bbe}"),
        ),
    ],
)
def test_should_serialize_import_messages_with_default_serializer(msg: object):
    # given / when
    result = default_serializer.serialize(msg)

    # then
    assert result is not None
