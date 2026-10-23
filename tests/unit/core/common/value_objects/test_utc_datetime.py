from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from app.core.common.exceptions import BusinessTypeError
from app.core.common.value_objects.utc_datetime import UtcDatetime


def test_normalizes_value_to_utc_when_input_has_offset() -> None:
    raw = datetime.fromisoformat("2024-01-01T03:00:00+03:00")

    sut = UtcDatetime(raw)

    assert sut.value.utcoffset() == timedelta(0)
    assert sut.value == datetime(2024, 1, 1, 0, 0, tzinfo=UTC)
    assert sut.value.timestamp() == raw.timestamp()


def test_preserves_same_timestamp_when_input_is_zoneinfo() -> None:
    raw = datetime(2024, 1, 15, 6, 0, tzinfo=ZoneInfo("Asia/Almaty"))

    sut = UtcDatetime(raw)

    assert sut.value.utcoffset() == timedelta(0)
    assert sut.value.timestamp() == raw.timestamp()


def test_raises_when_input_is_naive_datetime() -> None:
    raw = datetime.fromisoformat("2024-01-01T03:00:00")

    with pytest.raises(BusinessTypeError):
        UtcDatetime(raw)
