from datetime import timedelta

from app.core.common.value_objects.utc_datetime import UtcDatetime
from app.outbound.auth_ctx.model import AuthSession


class AuthSessionExpiryPolicy:
    def __init__(
        self,
        ttl: timedelta,
        refresh_threshold_ratio: float,
    ) -> None:
        self._ttl = ttl
        self._refresh_threshold_ratio = refresh_threshold_ratio

    def expiration_from(self, now: UtcDatetime) -> UtcDatetime:
        return UtcDatetime(now.value + self._ttl)

    def is_expired(self, session: AuthSession, *, now: UtcDatetime) -> bool:
        return session.expiration <= now

    def needs_refresh(self, session: AuthSession, *, now: UtcDatetime) -> bool:
        remaining = session.expiration.value - now.value
        return remaining <= self._ttl * self._refresh_threshold_ratio
