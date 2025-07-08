import pytest

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.services.authorization import AuthorizationService
from app.domain.enums.user_role import UserRole
from tests.app.unit.factories.user_entity import create_user


def test_user_can_act_on_himself() -> None:
    sut = AuthorizationService()
    user = create_user()

    sut.authorize_for_self(user.id_, target_id=user.id_)


def test_user_cannot_act_on_another_user() -> None:
    sut = AuthorizationService()
    user1 = create_user()
    user2 = create_user()

    with pytest.raises(AuthorizationError):
        sut.authorize_for_self(user1.id_, target_id=user2.id_)


@pytest.mark.parametrize(
    ("superior", "subordinate"),
    [
        (UserRole.SUPER_ADMIN, UserRole.ADMIN),
        (UserRole.SUPER_ADMIN, UserRole.USER),
        (UserRole.ADMIN, UserRole.USER),
    ],
)
def test_superior_role_can_act_on_subordinate(
    superior: UserRole,
    subordinate: UserRole,
) -> None:
    sut = AuthorizationService()

    sut.authorize_for_subordinate_role(superior, target_role=subordinate)


@pytest.mark.parametrize(
    "role",
    [
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN,
        UserRole.USER,
    ],
)
def test_peer_role_cannot_act_on_peer(
    role: UserRole,
) -> None:
    sut = AuthorizationService()

    with pytest.raises(AuthorizationError):
        sut.authorize_for_subordinate_role(role, target_role=role)


@pytest.mark.parametrize(
    ("inferior", "superior"),
    [
        (UserRole.USER, UserRole.ADMIN),
        (UserRole.USER, UserRole.SUPER_ADMIN),
        (UserRole.ADMIN, UserRole.SUPER_ADMIN),
    ],
)
def test_inferior_role_cannot_act_on_superior(
    inferior: UserRole,
    superior: UserRole,
) -> None:
    sut = AuthorizationService()

    with pytest.raises(AuthorizationError):
        sut.authorize_for_subordinate_role(inferior, target_role=superior)
