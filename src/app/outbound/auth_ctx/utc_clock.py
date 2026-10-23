from datetime import UTC, datetime

from app.core.common.value_objects.utc_datetime import UtcDatetime


class AuthUtcClock:
    @property
    def now(self) -> UtcDatetime:
        return UtcDatetime(datetime.now(UTC))
