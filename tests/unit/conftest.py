from uuid import UUID

import pytest

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import UserId, Username, UserPasswordHash


@pytest.fixture()
def sample_user() -> User:
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    username = "username"
    password_hash: bytes = "123456789abcdef0".encode()
    role = UserRoleEnum.USER
    is_active = True

    return User(
        id_=UserId(user_id),
        username=Username(username),
        password_hash=UserPasswordHash(password_hash),
        role=role,
        is_active=is_active,
    )


@pytest.fixture()
def other_sample_user() -> User:
    user_id = UUID("00000000-0000-0000-0000-000000000000")
    username = "username"
    password_hash: bytes = "123456789abcdef0".encode()
    role = UserRoleEnum.USER
    is_active = True

    return User(
        id_=UserId(user_id),
        username=Username(username),
        password_hash=UserPasswordHash(password_hash),
        role=role,
        is_active=is_active,
    )
