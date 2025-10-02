from abc import abstractmethod
from uuid import UUID


class UserIdGenerator:
    @abstractmethod
    def generate(self) -> UUID: ...
