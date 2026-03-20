import uuid
from datetime import UTC, datetime
from uuid import UUID

from app.core.common.entities.types_ import UserId, UserPasswordHash, UserRole
from app.core.common.entities.user import User
from app.core.common.ports.password_hasher import PasswordHasher
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime
from tests.unit.core.common.services.stubs import StubPasswordHasher


def create_user_id(value: UUID | None = None) -> UserId:
    return UserId(value if value is not None else uuid.uuid4())


def create_username(value: str | None = None) -> Username:
    default = f"user_{uuid.uuid4().hex[:8]}"
    return Username(value if value is not None else default)


def create_raw_password(value: str | None = None) -> RawPassword:
    default = uuid.uuid4().hex
    return RawPassword(value if value is not None else default)


def create_password_hash(value: bytes | None = None) -> UserPasswordHash:
    default = uuid.uuid4().bytes
    return UserPasswordHash(value if value is not None else default)


def create_now(value: datetime | None = None) -> UtcDatetime:
    default = datetime.now(UTC)
    return UtcDatetime(value if value is not None else default)


def create_role(value: str | None = None) -> UserRole:
    return UserRole(value) if value is not None else UserRole.USER


def create_is_active(value: bool | None = None) -> bool:
    return value if value is not None else True


def create_user_service(password_hasher: PasswordHasher | None = None) -> UserService:
    return UserService(password_hasher=password_hasher if password_hasher is not None else StubPasswordHasher())


def create_user(
    *,
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    now: UtcDatetime | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
) -> User:
    user_service = create_user_service()
    return user_service.create_user(
        user_id=user_id if user_id is not None else create_user_id(),
        username=username if username is not None else create_username(),
        password_hash=password_hash if password_hash is not None else create_password_hash(),
        now=now if now is not None else create_now(),
        role=role if role is not None else create_role(),
        is_active=is_active if is_active is not None else create_is_active(),
    )


def create_super_user(
    *,
    user_id: UserId | None = None,
    username: Username | None = None,
    password_hash: UserPasswordHash | None = None,
    now: UtcDatetime | None = None,
    is_active: bool | None = None,
) -> User:
    now_ = now if now is not None else create_now()
    return User(
        id_=user_id if user_id is not None else create_user_id(),
        username=username if username is not None else create_username(),
        password_hash=password_hash if password_hash is not None else create_password_hash(),
        role=UserRole.SUPER_ADMIN,
        is_active=is_active if is_active is not None else create_is_active(),
        created_at=now_,
        updated_at=now_,
    )
