from abc import abstractmethod
from typing import Protocol

from app.application.common.query_models.user import UserQueryModel
from app.application.common.query_params.user import UserListParams


class UserQueryGateway(Protocol):
    @abstractmethod
    async def read_all(
        self,
        user_read_all_params: UserListParams,
    ) -> list[UserQueryModel] | None:
        """
        :raises ReaderError:
        """
