import pytest

from app.common.c_infrastructure.custom_types import PasswordPepper
from app.distinct.user.c_infrastructure.adapters.password_hasher_bcrypt import (
    BcryptPasswordHasher,
)


@pytest.fixture
def bcrypt_password_hasher():
    return BcryptPasswordHasher(PasswordPepper("Habanero!"))
