from abc import abstractmethod

from app.common.b_application.id_generator import IdGenerator


class SessionIdGenerator(IdGenerator[str]):
    @abstractmethod
    def __call__(self) -> str: ...
