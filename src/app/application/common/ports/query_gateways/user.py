from abc import abstractmethod
from typing import Protocol

from app.application.common.query_filters.user.read_all import UserReadAllParams
from app.application.common.query_models.user import UserQueryModel


class UserQueryGateway(Protocol):
    @abstractmethod
    async def read_all(
        self, user_read_all_params: UserReadAllParams
    ) -> list[UserQueryModel] | None:
        """
        :raises ReaderError:
        """
