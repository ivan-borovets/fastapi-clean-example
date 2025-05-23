from abc import abstractmethod
from typing import Protocol

from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import UserId, Username


class UserCommandGateway(Protocol):
    @abstractmethod
    def add(self, user: User) -> None:
        """
        :raises DataMapperError:
        """

    @abstractmethod
    async def read_by_id(self, user_id: UserId) -> User | None:
        """
        :raises DataMapperError:
        """

    @abstractmethod
    async def read_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> User | None:
        """
        :raises DataMapperError:
        """
