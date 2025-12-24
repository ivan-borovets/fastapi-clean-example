from abc import abstractmethod

from app.domain.value_objects.user_id import UserId


class UserIdGenerator:
    @abstractmethod
    def generate(self) -> UserId: ...
