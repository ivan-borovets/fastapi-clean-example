from typing import cast
from unittest.mock import Mock, create_autospec
from uuid import UUID

import pytest

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    ActivationChangeNotPermitted,
    RoleChangeNotPermitted,
)
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username.username import Username


def create_user_service() -> UserService:
    return UserService(
        user_id_generator=create_autospec(UserIdGenerator),
        password_hasher=create_autospec(PasswordHasher),
    )


def test_create_user() -> None:
    user_service: UserService = create_user_service()
    username = Username("username")
    raw_password = RawPassword("securepassword")
    user_uuid = UUID("12345678-1234-5678-1234-567812345678")
    cast("Mock", user_service._user_id_generator).return_value = user_uuid
    password_hash_value = "mocked_password_hash".encode()
    cast("Mock", user_service._password_hasher.hash).return_value = password_hash_value

    user: User = user_service.create_user(username, raw_password)
    assert isinstance(user, User)
    assert user.id_ == UserId(user_uuid)
    assert user.username == username
    assert user.password_hash == UserPasswordHash(password_hash_value)
    assert user.role == UserRole.USER
    assert user.is_active


def test_is_password_valid(sample_user: User) -> None:
    user_service: UserService = create_user_service()
    password = RawPassword("test_password")
    verify_mock = cast("Mock", user_service._password_hasher.verify)

    verify_mock.return_value = True
    correct_result: bool = user_service.is_password_valid(sample_user, password)
    assert correct_result

    verify_mock.return_value = False
    incorrect_result: bool = user_service.is_password_valid(sample_user, password)
    assert not incorrect_result


def test_change_password(sample_user: User) -> None:
    user_service: UserService = create_user_service()
    raw_new_password = RawPassword("raw_new_password_to_be_hashed")
    hash_mock = cast("Mock", user_service._password_hasher.hash)
    original_password_hash: UserPasswordHash = sample_user.password_hash
    new_password_hash_value: bytes = "new_password_hash".encode()
    hash_mock.return_value = new_password_hash_value

    user_service.change_password(sample_user, raw_new_password)
    assert sample_user.password_hash != original_password_hash
    assert sample_user.password_hash == UserPasswordHash(new_password_hash_value)


def test_toggle_activation(sample_user: User) -> None:
    user_service: UserService = create_user_service()
    initial_state: bool = sample_user.is_active

    user_service.toggle_user_activation(sample_user, is_active=not initial_state)
    assert sample_user.is_active != initial_state

    user_service.toggle_user_activation(sample_user, is_active=initial_state)
    assert sample_user.is_active == initial_state

    sample_user.role = UserRole.SUPER_ADMIN
    with pytest.raises(ActivationChangeNotPermitted):
        user_service.toggle_user_activation(sample_user, is_active=True)
    with pytest.raises(ActivationChangeNotPermitted):
        user_service.toggle_user_activation(sample_user, is_active=False)


def test_toggle_admin_role(sample_user: User) -> None:
    user_service: UserService = create_user_service()

    user_service.toggle_user_admin_role(sample_user, is_admin=True)
    assert sample_user.role == UserRole.ADMIN

    user_service.toggle_user_admin_role(sample_user, is_admin=False)
    assert sample_user.role != UserRole.ADMIN

    sample_user.role = UserRole.SUPER_ADMIN
    with pytest.raises(RoleChangeNotPermitted):
        user_service.toggle_user_admin_role(sample_user, is_admin=True)
    with pytest.raises(RoleChangeNotPermitted):
        user_service.toggle_user_admin_role(sample_user, is_admin=False)
