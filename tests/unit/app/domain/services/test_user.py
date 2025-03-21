from typing import cast
from unittest.mock import Mock, create_autospec
from uuid import UUID

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import (
    RawPassword,
    UserId,
    Username,
    UserPasswordHash,
)
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService


def create_user_service() -> UserService:
    return UserService(
        user_id_generator=create_autospec(UserIdGenerator),
        password_hasher=create_autospec(PasswordHasher),
    )


def create_sample_user() -> User:
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


def test_create_user() -> None:
    user_service: UserService = create_user_service()
    username = Username("username")
    raw_password = RawPassword("securepassword")
    user_uuid = UUID("12345678-1234-5678-1234-567812345678")
    cast(Mock, user_service._user_id_generator).return_value = user_uuid
    password_hash_value = "mocked_password_hash".encode()
    cast(Mock, user_service._password_hasher.hash).return_value = password_hash_value

    user: User = user_service.create_user(username, raw_password)
    assert isinstance(user, User)
    assert user.id_ == UserId(user_uuid)
    assert user.username == username
    assert user.password_hash == UserPasswordHash(password_hash_value)
    assert user.role == UserRoleEnum.USER
    assert user.is_active


def test_is_password_valid() -> None:
    user_service: UserService = create_user_service()
    sample_user: User = create_sample_user()
    password = RawPassword("test_password")
    verify_mock = cast(Mock, user_service._password_hasher.verify)

    verify_mock.return_value = True
    correct_result: bool = user_service.is_password_valid(sample_user, password)
    assert correct_result

    verify_mock.return_value = False
    incorrect_result: bool = user_service.is_password_valid(sample_user, password)
    assert not incorrect_result


def test_change_password() -> None:
    user_service: UserService = create_user_service()
    sample_user: User = create_sample_user()
    raw_new_password = RawPassword("raw_new_password_to_be_hashed")
    hash_mock = cast(Mock, user_service._password_hasher.hash)
    original_password_hash: UserPasswordHash = sample_user.password_hash
    new_password_hash_value: bytes = "new_password_hash".encode()
    hash_mock.return_value = new_password_hash_value

    user_service.change_password(sample_user, raw_new_password)
    assert sample_user.password_hash != original_password_hash
    assert sample_user.password_hash == UserPasswordHash(new_password_hash_value)


def test_toggle_activation() -> None:
    user_service: UserService = create_user_service()
    sample_user: User = create_sample_user()
    initial_state: bool = sample_user.is_active

    user_service.toggle_user_activation(sample_user, not initial_state)
    assert sample_user.is_active != initial_state

    user_service.toggle_user_activation(sample_user, initial_state)
    assert sample_user.is_active == initial_state


def test_toggle_admin_role() -> None:
    user_service: UserService = create_user_service()
    sample_user: User = create_sample_user()

    user_service.toggle_user_admin_role(sample_user, True)
    assert sample_user.role == UserRoleEnum.ADMIN

    user_service.toggle_user_admin_role(sample_user, False)
    assert sample_user.role != UserRoleEnum.ADMIN
