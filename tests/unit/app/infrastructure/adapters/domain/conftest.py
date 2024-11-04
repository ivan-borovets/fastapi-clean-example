import pytest

from app.infrastructure.adapters.domain.bcrypt_password_hasher import (
    BcryptPasswordHasher,
)
from app.infrastructure.new_types import PasswordPepper


@pytest.fixture
def bcrypt_password_hasher():
    return BcryptPasswordHasher(PasswordPepper("Habanero!"))
