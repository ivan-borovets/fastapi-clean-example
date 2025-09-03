from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.user_id import UserId


class AccessRevoker(Protocol):
    @abstractmethod
    async def remove_all_user_access(self, user_id: UserId) -> None:
        """:raises DataMapperError:"""
