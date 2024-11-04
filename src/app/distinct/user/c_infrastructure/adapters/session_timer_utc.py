from datetime import UTC, datetime, timedelta

from app.common.c_infrastructure.custom_types import (
    JwtAccessTokenTtlMin,
    SessionRefreshThreshold,
)
from app.distinct.user.b_application.ports.session_timer import SessionTimer


class UtcSessionTimer(SessionTimer):
    def __init__(
        self,
        session_ttl_min: JwtAccessTokenTtlMin,
        session_refresh_threshold: SessionRefreshThreshold,
    ):
        self._session_ttl_min = session_ttl_min
        self._session_refresh_threshold = session_refresh_threshold

    @property
    def current_time(self) -> datetime:
        return datetime.now(tz=UTC)

    @property
    def access_expiration(self) -> datetime:
        return self.current_time + self._session_ttl_min

    @property
    def refresh_trigger_interval(self) -> timedelta:
        return self._session_ttl_min * self._session_refresh_threshold
