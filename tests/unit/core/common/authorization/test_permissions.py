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
from app.core.common.factories.id_factory import create_user_id
from tests.unit.core.common.authorization.factories import make_admin, make_super_admin, make_user
from tests.unit.core.common.services.factories import create_user


def test_can_manage_self() -> None:
    subject = create_user(user_id=create_user_id())
    context = UserManagementContext(subject=subject, target=subject)
    sut = CanManageSelf()

    assert sut.is_satisfied_by(context)


def test_cannot_manage_another_user() -> None:
    subject = create_user(user_id=create_user_id())
    target = create_user(user_id=create_user_id())
    context = UserManagementContext(subject=subject, target=target)
    sut = CanManageSelf()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_factory", "target_factory"),
    [
        pytest.param(make_super_admin, make_admin, id="super_admin_over_admin"),
        pytest.param(make_super_admin, make_user, id="super_admin_over_user"),
        pytest.param(make_admin, make_user, id="admin_over_user"),
    ],
)
def test_can_manage_subordinate(
    subject_factory: Callable[[], User],
    target_factory: Callable[[], User],
) -> None:
    context = UserManagementContext(subject=subject_factory(), target=target_factory())
    sut = CanManageSubordinate()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_factory", "target_factory"),
    [
        pytest.param(make_super_admin, make_super_admin, id="super_admin_over_super_admin"),
        pytest.param(make_admin, make_super_admin, id="admin_over_super_admin"),
        pytest.param(make_admin, make_admin, id="admin_over_admin"),
        pytest.param(make_user, make_admin, id="user_over_admin"),
    ],
)
def test_cannot_manage_non_subordinate(
    subject_factory: Callable[[], User],
    target_factory: Callable[[], User],
) -> None:
    context = UserManagementContext(subject=subject_factory(), target=target_factory())
    sut = CanManageSubordinate()

    assert not sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_factory", "target_role"),
    [
        pytest.param(make_super_admin, UserRole.ADMIN, id="super_admin_can_manage_admin_role"),
        pytest.param(make_super_admin, UserRole.USER, id="super_admin_can_manage_user_role"),
        pytest.param(make_admin, UserRole.USER, id="admin_can_manage_user_role"),
    ],
)
def test_can_manage_role(
    subject_factory: Callable[[], User],
    target_role: UserRole,
) -> None:
    context = RoleManagementContext(subject=subject_factory(), target_role=target_role)
    sut = CanManageRole()

    assert sut.is_satisfied_by(context)


@pytest.mark.parametrize(
    ("subject_factory", "target_role"),
    [
        pytest.param(make_super_admin, UserRole.SUPER_ADMIN, id="super_admin_cannot_manage_super_admin_role"),
        pytest.param(make_admin, UserRole.SUPER_ADMIN, id="admin_cannot_manage_super_admin_role"),
        pytest.param(make_admin, UserRole.ADMIN, id="admin_cannot_manage_admin_role"),
        pytest.param(make_user, UserRole.ADMIN, id="user_cannot_manage_admin_role"),
    ],
)
def test_cannot_manage_role(
    subject_factory: Callable[[], User],
    target_role: UserRole,
) -> None:
    context = RoleManagementContext(subject=subject_factory(), target_role=target_role)
    sut = CanManageRole()

    assert not sut.is_satisfied_by(context)
