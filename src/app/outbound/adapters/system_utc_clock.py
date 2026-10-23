from datetime import UTC, datetime

from app.core.common.ports.utc_clock import UtcClock
from app.core.common.value_objects.utc_datetime import UtcDatetime


class SystemUtcClock(UtcClock):
    @property
    def now(self) -> UtcDatetime:
        return UtcDatetime(datetime.now(UTC))
