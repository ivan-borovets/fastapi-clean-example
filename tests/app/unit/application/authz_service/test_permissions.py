import pytest

from app.application.common.services.authorization.permissions import (
    CanManageRole,
    CanManageSelf,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from app.domain.enums.user_role import UserRole
from tests.app.unit.factories.user_entity import create_user
from tests.app.unit.factories.value_objects import create_user_id


def test_can_manage_self() -> None:
    user_id = create_user_id()
    subject = create_user(user_id=user_id)
    target = create_user(user_id=user_id)
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert sut.is_satisfied_by(context)


def test_cannot_manage_another_user() -> None:
    subject_id = create_user_id()
    subject = create_user(user_id=subject_id)
    target_id = create_user_id()
    target = create_user(user_id=target_id)
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (UserRole.SUPER_ADMIN, UserRole.ADMIN),
        (UserRole.SUPER_ADMIN, UserRole.USER),
        (UserRole.ADMIN, UserRole.USER),
    ],
)
def test_can_manage_subordinate(
    subject_role: UserRole,
    target_role: UserRole,
) -> None:
    subject = create_user(role=subject_role)
    target = create_user(role=target_role)
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSubordinate()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN),
        (UserRole.ADMIN, UserRole.SUPER_ADMIN),
        (UserRole.ADMIN, UserRole.ADMIN),
        (UserRole.USER, UserRole.ADMIN),
    ],
)
def test_cannot_manage_non_subordinate(
    subject_role: UserRole,
    target_role: UserRole,
) -> None:
    subject = create_user(role=subject_role)
    target = create_user(role=target_role)
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSubordinate()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (UserRole.SUPER_ADMIN, UserRole.ADMIN),
        (UserRole.SUPER_ADMIN, UserRole.USER),
        (UserRole.ADMIN, UserRole.USER),
    ],
)
def test_can_manage_role(
    subject_role: UserRole,
    target_role: UserRole,
) -> None:
    subject = create_user(role=subject_role)
    context = RoleManagementContext(subject=subject, target_role=target_role)
    sut = CanManageRole()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_role", "target_role"),
    [
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN),
        (UserRole.ADMIN, UserRole.SUPER_ADMIN),
        (UserRole.ADMIN, UserRole.ADMIN),
        (UserRole.USER, UserRole.ADMIN),
    ],
)
def test_cannot_manage_role(
    subject_role: UserRole,
    target_role: UserRole,
) -> None:
    subject = create_user(role=subject_role)
    context = RoleManagementContext(subject=subject, target_role=target_role)
    sut = CanManageRole()

    assert not sut.is_satisfied_by(context)
