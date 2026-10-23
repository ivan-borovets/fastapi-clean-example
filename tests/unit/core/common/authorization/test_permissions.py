from collections.abc import Callable

import pytest

from app.core.common.authorization.permissions import (
    CanManageRole,
    CanManageSelf,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from tests.unit.core.common.services.factories import create_admin, create_super_admin, create_user


def test_can_manage_self() -> None:
    subject = create_user()
    context = UserManagementContext(subject=subject, target=subject)
    sut = CanManageSelf()

    assert sut.is_satisfied_by(context) is True


def test_cannot_manage_another_user() -> None:
    subject = create_user()
    target = create_user()
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert sut.is_satisfied_by(context) is False


@pytest.mark.parametrize(
    ("subject_factory", "target_factory"),
    [
        pytest.param(create_super_admin, create_admin, id="super_admin_over_admin"),
        pytest.param(create_super_admin, create_user, id="super_admin_over_user"),
        pytest.param(create_admin, create_user, id="admin_over_user"),
    ],
)
def test_can_manage_subordinate(
    subject_factory: Callable[[], User],
    target_factory: Callable[[], User],
) -> None:
    context = UserManagementContext(subject=subject_factory(), target=target_factory())
    sut = CanManageSubordinate()

    assert sut.is_satisfied_by(context) is True


@pytest.mark.parametrize(
    ("subject_factory", "target_factory"),
    [
        pytest.param(create_super_admin, create_super_admin, id="super_admin_over_super_admin"),
        pytest.param(create_admin, create_super_admin, id="admin_over_super_admin"),
        pytest.param(create_admin, create_admin, id="admin_over_admin"),
        pytest.param(create_user, create_admin, id="user_over_admin"),
    ],
)
def test_cannot_manage_non_subordinate(
    subject_factory: Callable[[], User],
    target_factory: Callable[[], User],
) -> None:
    context = UserManagementContext(subject=subject_factory(), target=target_factory())
    sut = CanManageSubordinate()

    assert sut.is_satisfied_by(context) is False


@pytest.mark.parametrize(
    ("subject_factory", "target_role"),
    [
        pytest.param(create_super_admin, UserRole.ADMIN, id="super_admin_can_manage_admin_role"),
        pytest.param(create_super_admin, UserRole.USER, id="super_admin_can_manage_user_role"),
        pytest.param(create_admin, UserRole.USER, id="admin_can_manage_user_role"),
    ],
)
def test_can_manage_role(
    subject_factory: Callable[[], User],
    target_role: UserRole,
) -> None:
    context = RoleManagementContext(subject=subject_factory(), target_role=target_role)
    sut = CanManageRole()

    assert sut.is_satisfied_by(context) is True


@pytest.mark.parametrize(
    ("subject_factory", "target_role"),
    [
        pytest.param(create_super_admin, UserRole.SUPER_ADMIN, id="super_admin_cannot_manage_super_admin_role"),
        pytest.param(create_admin, UserRole.SUPER_ADMIN, id="admin_cannot_manage_super_admin_role"),
        pytest.param(create_admin, UserRole.ADMIN, id="admin_cannot_manage_admin_role"),
        pytest.param(create_user, UserRole.ADMIN, id="user_cannot_manage_admin_role"),
    ],
)
def test_cannot_manage_role(
    subject_factory: Callable[[], User],
    target_role: UserRole,
) -> None:
    context = RoleManagementContext(subject=subject_factory(), target_role=target_role)
    sut = CanManageRole()

    assert sut.is_satisfied_by(context) is False
