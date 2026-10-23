from typing import Protocol
from unittest.mock import AsyncMock


class PasswordHasherMock(Protocol):
    hash: AsyncMock
    verify: AsyncMock
