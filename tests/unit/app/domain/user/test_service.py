from typing import cast
from unittest.mock import Mock
from uuid import UUID

from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.value_objects import Username, RawPassword


def test_create_user(user_service):
    user_service._user_id_generator.return_value = UUID(
        "12345678-1234-5678-1234-567812345678"
    )
    user_service._password_hasher.hash.return_value = "mocked_password_hash".encode()

    username = Username("testuser")
    raw_password = RawPassword("securepassword")

    user = user_service.create_user(username=username, raw_password=raw_password)

    assert isinstance(user, User)
    assert user.id_.value == UUID("12345678-1234-5678-1234-567812345678")
    assert user.username == username
    assert user.password_hash.value == "mocked_password_hash".encode()
    assert user.roles == {UserRoleEnum.USER}
    assert user.is_active

    cast(Mock, user_service._user_id_generator).assert_called_once()
    cast(Mock, user_service._password_hasher).hash.assert_called_once_with(raw_password)


def test_is_password_valid(user_service, sample_user):
    valid_password = RawPassword("correct_password")
    invalid_password = RawPassword("wrong_password")

    user_service._password_hasher.verify.return_value = True
    assert user_service.is_password_valid(sample_user, valid_password)

    cast(Mock, user_service)._password_hasher.verify.assert_called_with(
        raw_password=valid_password, hashed_password=sample_user.password_hash.value
    )

    user_service._password_hasher.verify.return_value = False
    assert not user_service.is_password_valid(sample_user, invalid_password)


def test_toggle_activation(user_service, sample_user):
    assert sample_user.is_active
    user_service.toggle_user_activation(sample_user, is_active=False)
    assert not sample_user.is_active

    user_service.toggle_user_activation(sample_user, is_active=True)
    assert sample_user.is_active


def test_toggle_admin_role(user_service, sample_user):
    assert UserRoleEnum.ADMIN not in sample_user.roles
    user_service.toggle_user_admin_role(sample_user, is_admin=True)
    assert UserRoleEnum.ADMIN in sample_user.roles

    user_service.toggle_user_admin_role(sample_user, is_admin=False)
    assert UserRoleEnum.ADMIN not in sample_user.roles
