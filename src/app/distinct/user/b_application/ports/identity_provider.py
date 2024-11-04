from abc import abstractmethod
from typing import Protocol

from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.vo_user import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_session(self) -> Session:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        """

    @abstractmethod
    async def get_current_user_id(self) -> UserId:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        """

    @abstractmethod
    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        :raises UserNotFoundById:
        """
