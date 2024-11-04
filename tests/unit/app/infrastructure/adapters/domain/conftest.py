import pytest

from app.infrastructure.new_types import PasswordPepper
from app.infrastructure.adapters.domain.bcrypt_password_hasher import BcryptPasswordHasher


@pytest.fixture
def bcrypt_password_hasher():
    return BcryptPasswordHasher(PasswordPepper("Habanero!"))
