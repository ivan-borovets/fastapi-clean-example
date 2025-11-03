import pytest

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from app.domain.services.user import UserService
from tests.app.unit.domain.services.mock_types import (
    PasswordHasherMock,
    UserIdGeneratorMock,
)
from tests.app.unit.factories.user_entity import create_user
from tests.app.unit.factories.value_objects import (
    create_password_hash,
    create_raw_password,
    create_user_id,
    create_username,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "role",
    [UserRole.USER, UserRole.ADMIN],
)
async def test_creates_active_user_with_hashed_password(
    role: UserRole,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    username = create_username()
    raw_password = create_raw_password()

    expected_id = create_user_id()
    expected_hash = create_password_hash()

    user_id_generator.generate.return_value = expected_id
    password_hasher.hash.return_value = expected_hash
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    result = await sut.create_user(username, raw_password, role)

    # Assert
    assert isinstance(result, User)
    assert result.id_ == expected_id
    assert result.username == username
    assert result.password_hash == expected_hash
    assert result.role == role
    assert result.is_active is True


@pytest.mark.asyncio
async def test_creates_inactive_user_if_specified(
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    username = create_username()
    raw_password = create_raw_password()
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    result = await sut.create_user(username, raw_password, is_active=False)

    assert not result.is_active


@pytest.mark.asyncio
async def test_fails_to_create_user_with_unassignable_role(
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    username = create_username()
    raw_password = create_raw_password()
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    with pytest.raises(RoleAssignmentNotPermittedError):
        await sut.create_user(
            username=username,
            raw_password=raw_password,
            role=UserRole.SUPER_ADMIN,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_valid",
    [True, False],
)
async def test_checks_password_authenticity(
    is_valid: bool,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    user = create_user()
    raw_password = create_raw_password()

    password_hasher.verify.return_value = is_valid
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    result = await sut.is_password_valid(user, raw_password)

    # Assert
    assert result is is_valid


@pytest.mark.asyncio
async def test_changes_password(
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    # Arrange
    initial_hash = create_password_hash(b"old")
    user = create_user(password_hash=initial_hash)
    raw_password = create_raw_password()

    expected_hash = create_password_hash(b"new")
    password_hasher.hash.return_value = expected_hash
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    # Act
    await sut.change_password(user, raw_password)

    # Assert
    assert user.password_hash == expected_hash


@pytest.mark.parametrize(
    ("initial_state", "target_state", "expected_result"),
    [
        pytest.param(True, False, True, id="active_to_inactive"),
        pytest.param(False, True, True, id="inactive_to_active"),
        pytest.param(True, True, False, id="already_active"),
        pytest.param(False, False, False, id="already_inactive"),
    ],
)
def test_toggles_activation_state(
    initial_state: bool,
    target_state: bool,
    expected_result: bool,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    user = create_user(is_active=initial_state)
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    result = sut.toggle_user_activation(user, is_active=target_state)

    assert result is expected_result
    assert user.is_active is target_state


@pytest.mark.parametrize(
    "is_active",
    [True, False],
)
def test_preserves_super_admin_activation_state(
    is_active: bool,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    user = create_user(role=UserRole.SUPER_ADMIN, is_active=not is_active)
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    with pytest.raises(ActivationChangeNotPermittedError):
        sut.toggle_user_activation(user, is_active=is_active)

    assert user.is_active is not is_active


@pytest.mark.parametrize(
    ("initial_role", "target_is_admin", "expected_role", "expected_result"),
    [
        pytest.param(UserRole.USER, True, UserRole.ADMIN, True, id="user_to_admin"),
        pytest.param(UserRole.ADMIN, False, UserRole.USER, True, id="admin_to_user"),
        pytest.param(UserRole.USER, False, UserRole.USER, False, id="already_user"),
        pytest.param(UserRole.ADMIN, True, UserRole.ADMIN, False, id="already_admin"),
    ],
)
def test_toggles_role(
    initial_role: UserRole,
    target_is_admin: bool,
    expected_role: UserRole,
    expected_result: bool,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    user = create_user(role=initial_role)
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    result = sut.toggle_user_admin_role(user, is_admin=target_is_admin)

    assert result is expected_result
    assert user.role == expected_role


@pytest.mark.parametrize(
    "is_admin",
    [True, False],
)
def test_preserves_super_admin_role(
    is_admin: bool,
    user_id_generator: UserIdGeneratorMock,
    password_hasher: PasswordHasherMock,
) -> None:
    user = create_user(role=UserRole.SUPER_ADMIN)
    sut = UserService(user_id_generator, password_hasher)  # type: ignore[arg-type]

    with pytest.raises(RoleChangeNotPermittedError):
        sut.toggle_user_admin_role(user, is_admin=is_admin)

    assert user.role == UserRole.SUPER_ADMIN
