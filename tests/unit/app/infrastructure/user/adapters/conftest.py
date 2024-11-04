import pytest

from app.infrastructure.custom_types import PasswordPepper
from app.infrastructure.user.adapters.password_hasher_bcrypt import BcryptPasswordHasher


@pytest.fixture
def bcrypt_password_hasher():
    return BcryptPasswordHasher(PasswordPepper("Habanero!"))
