from abc import abstractmethod
from typing import Protocol

from app.infrastructure.auth.session.model import AuthSession


class AuthSessionTransport(Protocol):
    @abstractmethod
    def deliver(self, auth_session: AuthSession) -> None: ...

    @abstractmethod
    def extract_id(self) -> str | None: ...

    @abstractmethod
    def remove_current(self) -> None: ...
