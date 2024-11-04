from abc import abstractmethod
from uuid import UUID

from app.common.b_application.id_generator import IdGenerator


class UserIdGenerator(IdGenerator[UUID]):
    @abstractmethod
    def __call__(self) -> UUID: ...
