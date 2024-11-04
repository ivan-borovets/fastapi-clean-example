from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Protocol


class SessionTimer(Protocol):
    _session_ttl_min: timedelta
    _session_refresh_threshold: float

    @property
    @abstractmethod
    def current_time(self) -> datetime: ...

    @property
    @abstractmethod
    def access_expiration(self) -> datetime: ...

    @property
    @abstractmethod
    def refresh_trigger_interval(self) -> timedelta: ...
