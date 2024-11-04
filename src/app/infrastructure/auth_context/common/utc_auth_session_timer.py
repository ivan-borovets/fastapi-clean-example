from datetime import UTC, datetime, timedelta

from app.infrastructure.auth_context.common.new_types import (
    AuthSessionRefreshThreshold,
    AuthSessionTtlMin,
)


class UtcAuthSessionTimer:
    def __init__(
        self,
        auth_session_ttl_min: AuthSessionTtlMin,
        auth_session_refresh_threshold: AuthSessionRefreshThreshold,
    ):
        self._auth_session_ttl_min = auth_session_ttl_min
        self._auth_session_refresh_threshold = auth_session_refresh_threshold

    @property
    def current_time(self) -> datetime:
        return datetime.now(tz=UTC)

    @property
    def access_expiration(self) -> datetime:
        return self.current_time + self._auth_session_ttl_min

    @property
    def refresh_trigger_interval(self) -> timedelta:
        return self._auth_session_ttl_min * self._auth_session_refresh_threshold
