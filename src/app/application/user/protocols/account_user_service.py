from abc import abstractmethod
from typing import Protocol

from app.domain.user.entity_user import User
from app.domain.user.vo_user import UserId, Username


class AccountUserService(Protocol):
    @abstractmethod
    async def check_username_uniqueness(self, username: Username) -> None:
        """
        :raises DataGatewayError:
        :raises UsernameAlreadyExists:
        """

    @abstractmethod
    async def create_user(self, username: Username, password: str) -> User: ...

    @abstractmethod
    async def save_user(self, user: User) -> None:
        """
        :raises DataGatewayError:
        """

    @abstractmethod
    async def get_user_by_username(
        self, username: Username, for_update: bool = False
    ) -> User:
        """
        :raises DataGatewayError:
        :raises UserNotFoundByUsername:
        """

    @abstractmethod
    async def get_user_by_id(self, user_id: UserId) -> User:
        """
        :raises DataGatewayError:
        :raises UserNotFoundById:
        """
