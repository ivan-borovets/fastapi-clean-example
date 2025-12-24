from abc import abstractmethod
from typing import Protocol

from app.domain.value_objects.user_id import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserId:
        """:raises AuthenticationError:"""
