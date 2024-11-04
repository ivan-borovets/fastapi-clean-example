from abc import abstractmethod

from app.application.id_generator import IdGenerator


class SessionIdGenerator(IdGenerator[str]):
    @abstractmethod
    def __call__(self) -> str: ...
