from datetime import UTC, datetime, timedelta


class UtcAuthSessionTimer:
    def __init__(self, ttl_min: timedelta, refresh_threshold: float) -> None:
        self._ttl_min = ttl_min
        self._refresh_threshold = refresh_threshold

    @property
    def current_time(self) -> datetime:
        return datetime.now(tz=UTC)

    @property
    def auth_session_expiration(self) -> datetime:
        return self.current_time + self._ttl_min

    @property
    def refresh_trigger_interval(self) -> timedelta:
        return self._ttl_min * self._refresh_threshold
