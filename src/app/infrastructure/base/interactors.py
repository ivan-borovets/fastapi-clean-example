"""
This module defines abstract interactors for encapsulating specific steps of a use case.

While single interactors are useful for isolating individual tasks,
consider creating an application service if your interactors handle
closely related actions or responsibilities.

Payloads (e.g., `SignInRequest` and `SignInResponse`)
should reside in the application layer.

Interactors are typically invoked by routers_controllers.

Example:
    from dataclasses import dataclass


    @dataclass(frozen=True, slots=True)
    class SignInRequest:
        ...

    @dataclass(frozen=True, slots=True)
    class SignInResponse:
        ...

    class SignInInteractor(InteractorStrict[SignInRequest, SignInResponse]):
        async def __call__(self, request_data: SignInRequest) -> SignInResponse:
            ...
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

RequestData = TypeVar("RequestData")
ResponseData = TypeVar("ResponseData")


class InteractorStrict(ABC, Generic[RequestData, ResponseData]):
    @abstractmethod
    async def __call__(self, request_data: RequestData) -> ResponseData: ...


class InteractorFlexible(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwargs: Any) -> dict[str, Any]: ...
