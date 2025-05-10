import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.services.authorization import AuthorizationService
from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum


def test_authorize_for_self(sample_user: User, other_sample_user: User) -> None:
    authz_service = AuthorizationService()
    current_user, target_user = sample_user, other_sample_user

    authz_service.authorize_for_self(current_user, target_user=current_user)

    with pytest.raises(AuthorizationError):
        authz_service.authorize_for_self(current_user, target_user=target_user)


@pytest.mark.parametrize(
    "current_role, target_role, should_pass",
    [
        (UserRoleEnum.USER, UserRoleEnum.USER, False),
        (UserRoleEnum.USER, UserRoleEnum.ADMIN, False),
        (UserRoleEnum.USER, UserRoleEnum.SUPER_ADMIN, False),
        (UserRoleEnum.ADMIN, UserRoleEnum.USER, True),
        (UserRoleEnum.ADMIN, UserRoleEnum.ADMIN, False),
        (UserRoleEnum.ADMIN, UserRoleEnum.SUPER_ADMIN, False),
        (UserRoleEnum.SUPER_ADMIN, UserRoleEnum.USER, True),
        (UserRoleEnum.SUPER_ADMIN, UserRoleEnum.ADMIN, True),
        (UserRoleEnum.SUPER_ADMIN, UserRoleEnum.SUPER_ADMIN, False),
    ],
)
def test_authorize_by_subordinate_role(
    current_role: UserRoleEnum,
    target_role: UserRoleEnum,
    should_pass: bool,
    sample_user: User,
    other_sample_user: User,
) -> None:
    authz_service = AuthorizationService()
    current_user, target_user = sample_user, other_sample_user
    current_user.role, target_user.role = current_role, target_role

    if should_pass:
        authz_service.authorize_for_subordinate_role(
            current_user, target_role=target_role
        )

    else:
        with pytest.raises(AuthorizationError):
            authz_service.authorize_for_subordinate_role(
                current_user, target_role=target_role
            )
