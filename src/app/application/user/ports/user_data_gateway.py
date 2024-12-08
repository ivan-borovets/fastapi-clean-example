from abc import abstractmethod
from typing import Protocol

from app.domain.user.entity import User
from app.domain.user.value_objects import UserId, Username


class UserDataGateway(Protocol):
    @abstractmethod
    async def save(self, user: User) -> None:
        """
        :raises DataGatewayError:
        """

    @abstractmethod
    async def read_by_id(self, user_id: UserId) -> User | None:
        """
        :raises DataGatewayError:
        """

    @abstractmethod
    async def read_by_username(
        self, username: Username, for_update: bool = False
    ) -> User | None:
        """
        :raises DataGatewayError:
        """

    @abstractmethod
    async def is_username_unique(self, username: Username) -> bool:
        """
        :raises DataGatewayError:
        """

    @abstractmethod
    async def read_all(self, limit: int, offset: int) -> list[User]:
        """
        :raises DataGatewayError:
        """
