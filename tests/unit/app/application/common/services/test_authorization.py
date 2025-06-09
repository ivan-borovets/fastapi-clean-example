import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.services.authorization import AuthorizationService
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


def test_authorize_for_self(sample_user: User, other_sample_user: User) -> None:
    authz_service = AuthorizationService()
    current_user, target_user = sample_user, other_sample_user

    authz_service.authorize_for_self(current_user.id_, target_id=current_user.id_)

    with pytest.raises(AuthorizationError):
        authz_service.authorize_for_self(current_user.id_, target_id=target_user.id_)


@pytest.mark.parametrize(
    ("current_role", "target_role", "should_pass"),
    [
        (UserRole.USER, UserRole.USER, False),
        (UserRole.USER, UserRole.ADMIN, False),
        (UserRole.USER, UserRole.SUPER_ADMIN, False),
        (UserRole.ADMIN, UserRole.USER, True),
        (UserRole.ADMIN, UserRole.ADMIN, False),
        (UserRole.ADMIN, UserRole.SUPER_ADMIN, False),
        (UserRole.SUPER_ADMIN, UserRole.USER, True),
        (UserRole.SUPER_ADMIN, UserRole.ADMIN, True),
        (UserRole.SUPER_ADMIN, UserRole.SUPER_ADMIN, False),
    ],
)
def test_authorize_by_subordinate_role(
    current_role: UserRole,
    target_role: UserRole,
    should_pass: bool,
) -> None:
    authz_service = AuthorizationService()

    if should_pass:
        authz_service.authorize_for_subordinate_role(
            current_role,
            target_role=target_role,
        )
    else:
        with pytest.raises(AuthorizationError):
            authz_service.authorize_for_subordinate_role(
                current_role,
                target_role=target_role,
            )
