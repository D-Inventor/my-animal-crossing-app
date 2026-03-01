from unittest.mock import AsyncMock

import pytest

from api.db.event_handler import EventHandlerCollection
from api.db.villager import VillagerCreated


@pytest.mark.asyncio
async def test_should_send_event_to_subscribed_handler():
    # given
    handler_collection = EventHandlerCollection()
    event_handler = AsyncMock()

    # when
    handler_collection.subscribe(event_handler)
    await handler_collection.publish([VillagerCreated(id="flg01")])

    # then
    event_handler.assert_called_once_with([VillagerCreated(id="flg01")])
