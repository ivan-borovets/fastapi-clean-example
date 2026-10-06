from datetime import datetime

from app.core.common.value_objects.utc_datetime import UtcDatetime


def nullable_utc_datetime(value: datetime | None) -> UtcDatetime | None:
    if value is None:
        return None
    return UtcDatetime(value)


def patch() -> None:
    if not hasattr(UtcDatetime, "__composite_values__"):
        setattr(  # noqa: B010
            UtcDatetime,
            "__composite_values__",
            lambda self: (self.value,),
        )
