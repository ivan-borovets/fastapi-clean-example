from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username import Username
from tests.app.unit.factories.value_objects import (
    create_password_hash,
    create_user_id,
    create_username,
)


def create_user(
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
) -> User:
    return User(
        id_=user_id or create_user_id(),
        username=username or create_username(),
        password_hash=password_hash or create_password_hash(),
        role=role,
        is_active=is_active,
    )
