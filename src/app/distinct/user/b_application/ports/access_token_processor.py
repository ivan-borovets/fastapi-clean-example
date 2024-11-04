from abc import abstractmethod
from typing import Protocol

from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.b_application.ports.session_timer import SessionTimer


class AccessTokenProcessor(Protocol):
    _session_timer: SessionTimer

    @abstractmethod
    def issue_access_token(self, session_id: SessionId) -> str: ...

    @abstractmethod
    def extract_session_id(self, access_token: str) -> SessionId:
        """
        :raises AdapterError:
        """
