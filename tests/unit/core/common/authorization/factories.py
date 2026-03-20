from app.core.common.entities.types_ import UserRole
from app.core.common.entities.user import User
from tests.unit.core.common.services.factories import create_super_user, create_user


def make_super_admin() -> User:
    return create_super_user()


def make_admin() -> User:
    return create_user(role=UserRole.ADMIN)


def make_user() -> User:
    return create_user(role=UserRole.USER)
