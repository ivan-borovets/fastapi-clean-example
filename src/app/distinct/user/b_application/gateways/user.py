from abc import abstractmethod
from typing import Protocol

from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.vo_user import UserId, Username


class UserGateway(Protocol):
    @abstractmethod
    async def create(self, user: User) -> None:
        """
        :raises GatewayError:
        """

    @abstractmethod
    async def read_by_id(self, user_id: UserId) -> User:
        """
        :raises UserNotFoundById:
        :raises GatewayError:
        """

    @abstractmethod
    async def read_by_username(self, username: Username) -> User:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """

    @abstractmethod
    async def is_username_unique(self, username: Username) -> bool:
        """
        :raises GatewayError:
        """

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> list[User]:
        """
        :raises GatewayError:
        """

    @abstractmethod
    async def set_activation_status_by_username(
        self, username: Username, is_active: bool
    ) -> None:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """

    @abstractmethod
    async def set_admin_status_by_username(
        self, username: Username, is_admin: bool
    ) -> None:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
