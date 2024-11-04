from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

RequestData = TypeVar("RequestData")
ResponseData = TypeVar("ResponseData")


class InteractorStrict(ABC, Generic[RequestData, ResponseData]):
    @abstractmethod
    async def __call__(self, request_data: RequestData) -> ResponseData: ...


class InteractorFlexible(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
