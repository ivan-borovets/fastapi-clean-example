from uuid import UUID

from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.vo_user import (
    UserId,
    Username,
    UserPasswordHash,
)


def test_user_init():
    user_id = UUID("12345678-1234-5678-1234-567812345678")
    username = "username"
    password_hash = bytes.fromhex("123456789abcdef0")
    roles = {UserRoleEnum.USER}
    is_active = True

    vo_user_id = UserId(user_id)
    vo_username = Username(username)
    vo_password_hash = UserPasswordHash(password_hash)

    direct_user = User(
        id_=vo_user_id,
        username=vo_username,
        password_hash=vo_password_hash,
        roles=roles,
        is_active=is_active,
    )

    indirect_user = User.create(
        user_id=user_id, username=username, password_hash=password_hash
    )

    assert isinstance(indirect_user, User)
    assert direct_user.id_ == vo_user_id == indirect_user.id_
    assert direct_user.username == vo_username == indirect_user.username
    assert direct_user.password_hash == vo_password_hash == indirect_user.password_hash


def test_user_activation(sample_user):
    assert sample_user.is_active
    sample_user.inactivate()
    assert not sample_user.is_active
    sample_user.activate()
    assert sample_user.is_active


def test_user_admin(sample_user):
    assert UserRoleEnum.ADMIN not in sample_user.roles
    sample_user.grant_admin()
    assert UserRoleEnum.ADMIN in sample_user.roles
    sample_user.revoke_admin()
    assert UserRoleEnum.ADMIN not in sample_user.roles
