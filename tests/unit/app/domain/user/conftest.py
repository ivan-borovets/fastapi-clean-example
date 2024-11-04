from typing import cast
from unittest.mock import Mock
from uuid import UUID

import pytest

from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.ports.password_hasher import PasswordHasher
from app.domain.user.service import UserService
from app.domain.user.value_objects import UserId, Username, UserPasswordHash


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
    mock_user_id_generator = Mock()
    mock_password_hasher = Mock()
    user_service = UserService(
        user_id_generator=mock_user_id_generator,
        password_hasher=cast(PasswordHasher, mock_password_hasher),
    )
    return user_service
