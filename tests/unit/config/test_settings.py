from datetime import timedelta

import pytest

from app.config.settings import SessionSettings


@pytest.mark.parametrize(
    ("ttl_min", "expected"),
    [
        pytest.param(1, timedelta(minutes=1), id="boundary"),
        pytest.param(5, timedelta(minutes=5), id="ordinary"),
    ],
)
def test_ttl_property_builds_timedelta(ttl_min: int, expected: timedelta) -> None:
    sut = SessionSettings(TTL_MIN=ttl_min)

    assert sut.ttl == expected
