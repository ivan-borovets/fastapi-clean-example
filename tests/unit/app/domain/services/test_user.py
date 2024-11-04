from typing import cast
from unittest.mock import Mock
from uuid import UUID

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import (
    RawPassword,
    UserId,
    Username,
    UserPasswordHash,
)
from app.domain.services.user import UserService


def test_create_user(user_service: UserService) -> None:
    username: Username = Username("username")
    raw_password: RawPassword = RawPassword("securepassword")

    user_uuid: UUID = UUID("12345678-1234-5678-1234-567812345678")
    cast(Mock, user_service._user_id_generator).return_value = user_uuid

    password_hash_value: bytes = "mocked_password_hash".encode()
    cast(Mock, user_service._password_hasher.hash).return_value = password_hash_value

    user: User = user_service.create_user(username, raw_password)

    cast(Mock, user_service._user_id_generator).assert_called_once()
    cast(Mock, user_service._password_hasher.hash).assert_called_once_with(raw_password)

    assert isinstance(user, User)

    assert user.id_ == UserId(user_uuid)
    assert user.username == username
    assert user.password_hash == UserPasswordHash(password_hash_value)
    assert user.role == UserRoleEnum.USER
    assert user.is_active


def test_is_password_valid(user_service: UserService, sample_user: User) -> None:
    password: RawPassword = RawPassword("test_password")
    verify_mock: Mock = cast(Mock, user_service._password_hasher.verify)

    verify_mock.return_value = True
    correct_result: bool = user_service.is_password_valid(sample_user, password)
    assert correct_result

    verify_mock.return_value = False
    incorrect_result: bool = user_service.is_password_valid(sample_user, password)
    assert not incorrect_result

    verify_mock.assert_called_with(
        raw_password=password, hashed_password=sample_user.password_hash.value
    )
    assert verify_mock.call_count == 2


def test_change_password(user_service: UserService, sample_user: User) -> None:
    raw_new_password: RawPassword = RawPassword("raw_new_password_to_be_hashed")
    hash_mock: Mock = cast(Mock, user_service._password_hasher.hash)

    original_password_hash: UserPasswordHash = sample_user.password_hash
    new_password_hash_value: bytes = "new_password_hash".encode()
    hash_mock.return_value = new_password_hash_value

    user_service.change_password(sample_user, raw_new_password)

    hash_mock.assert_called_once_with(raw_new_password)
    assert sample_user.password_hash != original_password_hash
    assert sample_user.password_hash == UserPasswordHash(new_password_hash_value)


def test_toggle_activation(user_service: UserService, sample_user: User) -> None:
    initial_state: bool = sample_user.is_active

    user_service.toggle_user_activation(sample_user, not initial_state)
    assert sample_user.is_active != initial_state

    user_service.toggle_user_activation(sample_user, initial_state)
    assert sample_user.is_active == initial_state


def test_toggle_admin_role(user_service: UserService, sample_user: User) -> None:
    user_service.toggle_user_admin_role(sample_user, True)
    assert sample_user.role == UserRoleEnum.ADMIN

    user_service.toggle_user_admin_role(sample_user, False)
    assert sample_user.role != UserRoleEnum.ADMIN
