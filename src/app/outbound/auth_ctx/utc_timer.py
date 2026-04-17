from datetime import UTC, datetime, timedelta

from app.core.common.value_objects.utc_datetime import UtcDatetime
from app.outbound.auth_ctx.model import AuthSession


class AuthSessionUtcTimer:
    def __init__(
        self,
        ttl: timedelta,
        refresh_threshold_ratio: float,
    ) -> None:
        self._ttl = ttl
        self._refresh_threshold_ratio = refresh_threshold_ratio

    @property
    def now(self) -> UtcDatetime:
        return UtcDatetime(datetime.now(UTC))

    @property
    def expiration_from_now(self) -> UtcDatetime:
        return UtcDatetime(self.now.value + self._ttl)

    def is_expired(self, session: AuthSession) -> bool:
        return session.expiration.value <= self.now.value

    def needs_refresh(self, session: AuthSession) -> bool:
        remaining = session.expiration.value - self.now.value
        return remaining <= self._ttl * self._refresh_threshold_ratio
