from abc import abstractmethod
from typing import Protocol

from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.username.username import Username


class UserDataGateway(Protocol):
    """
    Defined to allow easier mocking and swapping
    of implementations in the same layer.
    """

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
    async def read_by_username(self, username: Username) -> User | None:
        """
        :raises DataMapperError:
        """
