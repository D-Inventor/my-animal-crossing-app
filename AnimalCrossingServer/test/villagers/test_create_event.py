from api.db.villager import Villager, VillagerCreated


def test_should_create_event_when_creating_villager():

    # given
    entity = Villager.create(id="flg01", name="Ribbot")

    # when
    result = entity.consume_events()

    # then
    assert VillagerCreated(id="flg01") in result


def test_should_only_be_able_to_consume_events_once():

    # given
    entity = Villager.create(id="flg01", name="Ribbot")
    entity.consume_events()

    # when
    result = entity.consume_events()

    # then
    assert len(result) == 0
