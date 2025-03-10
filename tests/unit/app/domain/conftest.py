from unittest.mock import create_autospec
from uuid import UUID

import pytest

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import UserId, Username, UserPasswordHash
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService


@pytest.fixture
def sample_user() -> User:
    user_id: UUID = UUID("12345678-1234-5678-1234-567812345678")
    username: str = "username"
    password_hash: bytes = "123456789abcdef0".encode()
    role: UserRoleEnum = UserRoleEnum.USER
    is_active: bool = True

    return User(
        id_=UserId(user_id),
        username=Username(username),
        password_hash=UserPasswordHash(password_hash),
        role=role,
        is_active=is_active,
    )


@pytest.fixture
def user_service() -> UserService:
    return UserService(
        user_id_generator=create_autospec(UserIdGenerator),
        password_hasher=create_autospec(PasswordHasher),
    )
