from typing import Protocol
from unittest.mock import AsyncMock, Mock


class UserIdGeneratorMock(Protocol):
    generate: Mock


class PasswordHasherMock(Protocol):
    hash: AsyncMock
    verify: AsyncMock
