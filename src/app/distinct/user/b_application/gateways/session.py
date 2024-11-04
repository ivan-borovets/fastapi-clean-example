from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.a_domain.vo_user import UserId


class SessionGateway(Protocol):
    @abstractmethod
    async def create(self, session: Session) -> None:
        """
        ":raises GatewayError:"
        """

    @abstractmethod
    async def read_by_id(self, session_id: SessionId) -> Session:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """

    @abstractmethod
    async def update_expiration_by_id(
        self, session_id: SessionId, new_expiration: datetime
    ) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """

    @abstractmethod
    async def delete_by_id(self, session_id: SessionId) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """

    @abstractmethod
    async def delete_all_of_user_id(self, user_id: UserId) -> None:
        """
        :raises GatewayError:
        """
