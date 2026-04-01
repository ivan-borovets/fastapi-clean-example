import uuid
from datetime import UTC, datetime

from app.core.common.entities.types_ import UserId, UserPasswordHash, UserRole
from app.core.common.entities.user import User
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime


def create_raw_user_id(value: uuid.UUID | None = None) -> uuid.UUID:
    return value if value is not None else uuid.uuid4()


def create_raw_username(value: str | None = None) -> str:
    return value if value is not None else f"user_{uuid.uuid4().hex[:8]}"


def create_raw_password(value: str | None = None) -> str:
    return value if value is not None else uuid.uuid4().hex


def create_raw_password_hash(value: bytes | None = None) -> bytes:
    return value if value is not None else uuid.uuid4().bytes


def create_raw_now(value: datetime | None = None) -> datetime:
    if value is not None:
        UtcDatetime(value)
        return value
    return datetime.now(UTC)


def create_user(
    user_service: UserService,
    *,
    raw_user_id: uuid.UUID | None = None,
    raw_username: str | None = None,
    raw_password_hash: bytes | None = None,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
    raw_now: datetime | None = None,
) -> User:
    now = UtcDatetime(raw_now if raw_now is not None else create_raw_now())
    return user_service.create_user(
        user_id=UserId(raw_user_id if raw_user_id is not None else create_raw_user_id()),
        username=Username(raw_username if raw_username is not None else create_raw_username()),
        password_hash=UserPasswordHash(
            raw_password_hash if raw_password_hash is not None else create_raw_password_hash()
        ),
        now=now,
        role=role,
        is_active=is_active,
    )


async def create_user_with_password(
    user_service: UserService,
    *,
    raw_user_id: uuid.UUID | None = None,
    raw_username: str | None = None,
    raw_password: str | None = None,
    role: UserRole = UserRole.USER,
    is_active: bool = True,
    raw_now: datetime | None = None,
) -> User:
    now = UtcDatetime(raw_now if raw_now is not None else create_raw_now())
    return await user_service.create_user_with_raw_password(
        user_id=UserId(raw_user_id if raw_user_id is not None else create_raw_user_id()),
        username=Username(raw_username if raw_username is not None else create_raw_username()),
        raw_password=RawPassword(raw_password if raw_password is not None else create_raw_password()),
        now=now,
        role=role,
        is_active=is_active,
    )


async def create_super_admin_with_password(
    user_service: UserService,
    *,
    raw_user_id: uuid.UUID | None = None,
    raw_username: str | None = None,
    raw_password: str | None = None,
    is_active: bool = True,
    raw_now: datetime | None = None,
) -> User:
    """System role is not assignable via UserService; create as USER, then promote."""
    user = await create_user_with_password(
        user_service,
        raw_user_id=raw_user_id,
        raw_username=raw_username,
        raw_password=raw_password,
        is_active=is_active,
        raw_now=raw_now,
    )
    user.role = UserRole.SUPER_ADMIN
    return user
