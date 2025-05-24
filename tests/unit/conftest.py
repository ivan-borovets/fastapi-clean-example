from uuid import UUID

import pytest

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username.username import Username


@pytest.fixture
def sample_user() -> User:
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    username = "username"
    password_hash: bytes = "123456789abcdef0".encode()
    role = UserRole.USER
    is_active = True

    return User(
        id_=UserId(user_id),
        username=Username(username),
        password_hash=UserPasswordHash(password_hash),
        role=role,
        is_active=is_active,
    )


@pytest.fixture
def other_sample_user() -> User:
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    username = "username"
    password_hash: bytes = "123456789abcdef0".encode()
    role = UserRole.USER
    is_active = True

    return User(
        id_=UserId(user_id),
        username=Username(username),
        password_hash=UserPasswordHash(password_hash),
        role=role,
        is_active=is_active,
    )
