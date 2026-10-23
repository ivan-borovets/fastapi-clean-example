import uuid
from uuid import UUID

from app.core.common.entities.types_ import UserId, UserPasswordHash, UserRole
from app.core.common.entities.user import User
from app.core.common.ports.password_hasher import PasswordHasher
from app.core.common.services.user import UserService
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime
from tests.unit.core.common.services.stubs import StubPasswordHasher
from tests.unit.core.common.value_objects.factories import create_username, create_utc_datetime


def create_user_id(value: UUID | None = None) -> UserId:
    return UserId(value if value is not None else uuid.uuid4())


def create_user_password_hash(value: bytes | None = None) -> UserPasswordHash:
    default = uuid.uuid4().bytes
    return UserPasswordHash(value if value is not None else default)


def create_user_service(password_hasher: PasswordHasher | None = None) -> UserService:
    return UserService(password_hasher=password_hasher if password_hasher is not None else StubPasswordHasher())


def create_user(
    *,
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    now: UtcDatetime | None = None,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
) -> User:
    user_service = create_user_service()
    return user_service.create_user(
        user_id=user_id if user_id is not None else create_user_id(),
        username=username if username is not None else create_username(),
        password_hash=password_hash if password_hash is not None else create_user_password_hash(),
        now=now if now is not None else create_utc_datetime(),
        role=role,
        is_active=is_active,
    )


def create_admin(
    *,
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    now: UtcDatetime | None = None,
    is_active: bool = True,
) -> User:
    return create_user(
        user_id=user_id,
        username=username,
        password_hash=password_hash,
        now=now,
        role=UserRole.ADMIN,
        is_active=is_active,
    )


def create_super_admin(
    *,
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    now: UtcDatetime | None = None,
    is_active: bool = True,
) -> User:
    """System role is not assignable via UserService; create as USER, then promote."""
    user = create_user(
        user_id=user_id,
        username=username,
        password_hash=password_hash,
        now=now,
        is_active=is_active,
    )
    user.role = UserRole.SUPER_ADMIN
    return user
