from typing import cast
from unittest.mock import MagicMock, create_autospec

import pytest

from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator


@pytest.fixture
def user_id_generator() -> MagicMock:
    return cast(MagicMock, create_autospec(UserIdGenerator))


@pytest.fixture
def password_hasher() -> MagicMock:
    return cast(MagicMock, create_autospec(PasswordHasher))
