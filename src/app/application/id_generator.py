from abc import abstractmethod
from typing import Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)


class IdGenerator(Protocol[T_co]):
    @abstractmethod
    def __call__(self) -> T_co: ...
