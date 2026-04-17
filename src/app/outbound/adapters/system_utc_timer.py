from datetime import UTC, datetime

from app.core.commands.ports.utc_timer import UtcTimer
from app.core.common.value_objects.utc_datetime import UtcDatetime


class SystemUtcTimer(UtcTimer):
    @property
    def now(self) -> UtcDatetime:
        return UtcDatetime(datetime.now(UTC))
