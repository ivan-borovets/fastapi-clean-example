from abc import abstractmethod
from typing import Protocol


class AccessTokenRequestHandler(Protocol):
    @abstractmethod
    def get_access_token_from_request(self) -> str | None: ...

    @abstractmethod
    def add_access_token_to_request(self, new_access_token: str) -> None: ...

    @abstractmethod
    def delete_access_token_from_request(self) -> None: ...
