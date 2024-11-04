from abc import abstractmethod
from uuid import UUID


class UserIdGenerator:
    @abstractmethod
    def __call__(self) -> UUID: ...
