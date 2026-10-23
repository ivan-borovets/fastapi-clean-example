from datetime import timedelta

import pytest

from app.core.common.entities.types_ import UserRole
from app.core.common.exceptions import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from tests.unit.core.common.services.factories import (
    create_super_admin,
    create_user,
    create_user_id,
    create_user_password_hash,
    create_user_service,
)
from tests.unit.core.common.services.mock_types import PasswordHasherMock
from tests.unit.core.common.value_objects.factories import create_raw_password, create_username, create_utc_datetime


@pytest.mark.parametrize(
    "role",
    [UserRole.USER, UserRole.ADMIN],
)
async def test_creates_active_user_with_hashed_password(
    role: UserRole,
    password_hasher: PasswordHasherMock,
) -> None:
    sut = create_user_service(password_hasher=password_hasher)
    user_id = create_user_id()
    username = create_username()
    raw_password = create_raw_password()
    expected_hash = create_user_password_hash()
    created_at = create_utc_datetime()
    password_hasher.hash.return_value = expected_hash

    user = await sut.create_user_with_raw_password(
        user_id=user_id,
        username=username,
        raw_password=raw_password,
        now=created_at,
        role=role,
    )

    assert user.id_ == user_id
    assert user.username == username
    assert user.password_hash == expected_hash
    assert user.role == role
    assert user.is_active is True
    assert user.created_at == created_at
    assert user.updated_at == created_at


async def test_creates_inactive_user_when_requested() -> None:
    sut = create_user_service()
    user_id = create_user_id()
    username = create_username()
    raw_password = create_raw_password()

    user = await sut.create_user_with_raw_password(
        user_id=user_id,
        username=username,
        raw_password=raw_password,
        now=create_utc_datetime(),
        is_active=False,
    )

    assert user.is_active is False


async def test_fails_to_create_user_with_unassignable_role() -> None:
    sut = create_user_service()
    user_id = create_user_id()
    username = create_username()
    raw_password = create_raw_password()

    with pytest.raises(RoleAssignmentNotPermittedError):
        await sut.create_user_with_raw_password(
            user_id=user_id,
            username=username,
            raw_password=raw_password,
            now=create_utc_datetime(),
            role=UserRole.SUPER_ADMIN,
        )


async def test_accepts_correct_password() -> None:
    sut = create_user_service()
    password = create_raw_password()
    user = await sut.create_user_with_raw_password(
        user_id=create_user_id(),
        username=create_username(),
        raw_password=password,
        now=create_utc_datetime(),
    )

    is_password_valid = await sut.is_password_valid(user, password)

    assert is_password_valid is True


async def test_rejects_incorrect_password() -> None:
    sut = create_user_service()
    user = await sut.create_user_with_raw_password(
        user_id=create_user_id(),
        username=create_username(),
        raw_password=create_raw_password(),
        now=create_utc_datetime(),
    )

    is_password_valid = await sut.is_password_valid(user, create_raw_password())

    assert is_password_valid is False


async def test_changes_password() -> None:
    sut = create_user_service()
    old_password = create_raw_password()
    user = await sut.create_user_with_raw_password(
        user_id=create_user_id(),
        username=create_username(),
        raw_password=old_password,
        now=create_utc_datetime(),
    )
    new_password = create_raw_password()
    updated_at = create_utc_datetime()

    await sut.change_password(user, new_password, now=updated_at)

    is_new_password_valid = await sut.is_password_valid(user, new_password)
    is_old_password_valid = await sut.is_password_valid(user, old_password)
    assert is_new_password_valid is True
    assert is_old_password_valid is False
    assert user.updated_at == updated_at


@pytest.mark.parametrize(
    ("initial_role", "target_is_admin", "expected_role"),
    [
        pytest.param(UserRole.USER, True, UserRole.ADMIN, id="user_to_admin"),
        pytest.param(UserRole.ADMIN, False, UserRole.USER, id="admin_to_user"),
    ],
)
def test_set_role_changes_role_when_needed(
    *,
    initial_role: UserRole,
    target_is_admin: bool,
    expected_role: UserRole,
) -> None:
    sut = create_user_service()
    user = create_user(role=initial_role)
    updated_at = create_utc_datetime()

    result = sut.set_role(user, now=updated_at, is_admin=target_is_admin)

    assert result is True
    assert user.role == expected_role
    assert user.updated_at == updated_at


@pytest.mark.parametrize(
    ("role", "is_admin"),
    [
        pytest.param(UserRole.USER, False, id="already_user"),
        pytest.param(UserRole.ADMIN, True, id="already_admin"),
    ],
)
def test_set_role_does_nothing_when_already_in_target_role(
    *,
    role: UserRole,
    is_admin: bool,
) -> None:
    sut = create_user_service()
    created_at = create_utc_datetime()
    user = create_user(role=role, now=created_at)
    attempt_at = create_utc_datetime(created_at.value + timedelta(hours=1))

    result = sut.set_role(user, now=attempt_at, is_admin=is_admin)

    assert result is False
    assert user.role == role
    assert user.updated_at == created_at


@pytest.mark.parametrize(
    "is_admin",
    [True, False],
)
def test_preserves_super_admin_role(*, is_admin: bool) -> None:
    sut = create_user_service()
    created_at = create_utc_datetime()
    user = create_super_admin(now=created_at)
    attempt_at = create_utc_datetime(created_at.value + timedelta(hours=1))

    with pytest.raises(RoleChangeNotPermittedError):
        sut.set_role(user, now=attempt_at, is_admin=is_admin)

    assert user.role == UserRole.SUPER_ADMIN
    assert user.updated_at == created_at


@pytest.mark.parametrize(
    ("initial_state", "target_state"),
    [
        pytest.param(True, False, id="active_to_inactive"),
        pytest.param(False, True, id="inactive_to_active"),
    ],
)
def test_set_activation_changes_state_when_needed(
    *,
    initial_state: bool,
    target_state: bool,
) -> None:
    sut = create_user_service()
    user = create_user(is_active=initial_state)
    updated_at = create_utc_datetime()

    result = sut.set_activation(user, now=updated_at, is_active=target_state)

    assert result is True
    assert user.is_active is target_state
    assert user.updated_at == updated_at


@pytest.mark.parametrize(
    "state",
    [
        pytest.param(True, id="already_active"),
        pytest.param(False, id="already_inactive"),
    ],
)
def test_set_activation_does_nothing_when_already_in_target_state(*, state: bool) -> None:
    sut = create_user_service()
    created_at = create_utc_datetime()
    user = create_user(is_active=state, now=created_at)
    attempt_at = create_utc_datetime(created_at.value + timedelta(hours=1))

    result = sut.set_activation(user, now=attempt_at, is_active=state)

    assert result is False
    assert user.is_active is state
    assert user.updated_at == created_at


@pytest.mark.parametrize(
    "is_active",
    [True, False],
)
def test_preserves_super_admin_activation_state(*, is_active: bool) -> None:
    sut = create_user_service()
    created_at = create_utc_datetime()
    user = create_super_admin(now=created_at, is_active=is_active)
    attempt_at = create_utc_datetime(created_at.value + timedelta(hours=1))

    with pytest.raises(ActivationChangeNotPermittedError):
        sut.set_activation(user, now=attempt_at, is_active=not is_active)

    assert user.is_active is is_active
    assert user.updated_at == created_at
