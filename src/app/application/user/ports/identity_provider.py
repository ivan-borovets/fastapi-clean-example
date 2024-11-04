from abc import abstractmethod
from typing import Protocol

from app.domain.user.enums import UserRoleEnum
from app.domain.user.vo_user import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserId:
        """
        :raises AdapterError:
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        :raises SessionExpired:
        """

    @abstractmethod
    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AdapterError:
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        :raises SessionExpired:
        :raises UserNotFoundById:
        """
