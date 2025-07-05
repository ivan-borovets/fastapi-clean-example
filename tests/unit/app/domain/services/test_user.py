from unittest.mock import MagicMock

import pytest

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    RoleChangeNotPermittedError,
)
from app.domain.services.user import UserService
from tests.unit.app.factories.user_entity import create_user
from tests.unit.app.factories.value_objects import (
    create_password_hash,
    create_raw_password,
    create_user_id,
    create_username,
)


def test_creates_active_regular_user_with_hashed_password(
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    # Arrange
    username = create_username()
    raw_password = create_raw_password()

    expected_id = create_user_id()
    expected_hash = create_password_hash()

    user_id_generator.return_value = expected_id.value
    password_hasher.hash.return_value = expected_hash.value
    sut = UserService(user_id_generator, password_hasher)

    # Act
    result = sut.create_user(username, raw_password)

    # Assert
    assert isinstance(result, User)
    assert result.id_ == expected_id
    assert result.username == username
    assert result.password_hash == expected_hash
    assert result.role == UserRole.USER
    assert result.is_active is True


@pytest.mark.parametrize(
    "is_valid",
    [True, False],
)
def test_checks_password_authenticity(
    is_valid: bool,
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    # Arrange
    user = create_user()
    raw_password = create_raw_password()

    password_hasher.verify.return_value = is_valid
    sut = UserService(user_id_generator, password_hasher)

    # Act
    result = sut.is_password_valid(user, raw_password)

    # Assert
    assert result is is_valid


def test_changes_password(
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    # Arrange
    initial_hash = create_password_hash(b"old")
    user = create_user(password_hash=initial_hash)
    raw_password = create_raw_password()

    expected_hash = create_password_hash(b"new")
    password_hasher.hash.return_value = expected_hash.value
    sut = UserService(user_id_generator, password_hasher)

    # Act
    sut.change_password(user, raw_password)

    # Assert
    assert user.password_hash == expected_hash


@pytest.mark.parametrize(
    "is_active",
    [True, False],
)
def test_toggles_activation_state(
    is_active: bool,
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    user = create_user(is_active=not is_active)
    sut = UserService(user_id_generator, password_hasher)

    sut.toggle_user_activation(user, is_active=is_active)

    assert user.is_active is is_active


@pytest.mark.parametrize(
    "is_active",
    [True, False],
)
def test_preserves_super_admin_activation_state(
    is_active: bool,
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    user = create_user(role=UserRole.SUPER_ADMIN, is_active=not is_active)
    sut = UserService(user_id_generator, password_hasher)

    with pytest.raises(ActivationChangeNotPermittedError):
        sut.toggle_user_activation(user, is_active=is_active)

    assert user.is_active is not is_active


@pytest.mark.parametrize(
    "is_admin",
    [True, False],
)
def test_toggles_role(
    is_admin: bool,
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    user = create_user()
    sut = UserService(user_id_generator, password_hasher)

    sut.toggle_user_admin_role(user, is_admin=is_admin)

    assert user.role == UserRole.ADMIN if is_admin else UserRole.USER


@pytest.mark.parametrize(
    "is_admin",
    [True, False],
)
def test_preserves_super_admin_role(
    is_admin: bool,
    user_id_generator: MagicMock,
    password_hasher: MagicMock,
) -> None:
    user = create_user(role=UserRole.SUPER_ADMIN)
    sut = UserService(user_id_generator, password_hasher)

    with pytest.raises(RoleChangeNotPermittedError):
        sut.toggle_user_admin_role(user, is_admin=is_admin)

    assert user.role == UserRole.SUPER_ADMIN
