from datetime import datetime, timedelta, timezone

import pytest

from import_worker.db.snapshot import UtcDatetime, VillagerSnapshot


def test_should_not_accept_nonutc_datetime():
    # given
    now = datetime(2026, 3, 29, 12, 0, 0, 0, timezone(timedelta(hours=3), "EEST"))

    # when / then
    with pytest.raises(ValueError):
        UtcDatetime(datetime=now)


def test_should_add_timedelta():
    # given
    now = UtcDatetime(datetime=datetime(2026, 3, 29, 12, 0, 0, 0, timezone.utc))
    delta = timedelta(hours=1)

    # when
    result = now + delta

    # then
    expected = datetime(2026, 3, 29, 13, 0, 0, 0, timezone.utc)
    assert result.datetime == expected


def test_should_compare_with_datetime():
    # given
    now = datetime(2026, 3, 29, 12, 0, 0, 0, timezone.utc)
    utcnow = UtcDatetime(now)

    # when / then
    assert now == utcnow


def test_should_compare_with_other_utcdatetime():
    # given
    now = datetime(2026, 3, 29, 12, 0, 0, 0, timezone.utc)
    utcnowfirst = UtcDatetime(now)
    utcnowsecond = UtcDatetime(now)

    # when / then
    assert utcnowfirst == utcnowsecond


def test_should_create_snapshot_with_given_date():
    # given / when
    now = UtcDatetime(datetime(2026, 3, 29, 12, 0, 0, 0, timezone.utc))
    entity = VillagerSnapshot.create(now)

    # then
    assert entity.started_on == now


def test_should_finish_on_given_date():
    # given
    start_time = UtcDatetime(datetime=datetime(2026, 3, 29, 12, 0, 0, 0, timezone.utc))
    villager = VillagerSnapshot.create(start_time)

    # when
    finish_time = start_time + timedelta(hours=1)
    villager.finish(finish_time)

    # then
    assert villager.finished_on == finish_time.datetime
