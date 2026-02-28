from app.core.common.entities.types_ import UserId, UserPasswordHash, UserRole
from app.core.common.entities.user import User
from app.core.common.exceptions import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
)
from app.core.common.ports.password_hasher import PasswordHasher
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username
from app.core.common.value_objects.utc_datetime import UtcDatetime


class UserService:
    def __init__(self, password_hasher: PasswordHasher) -> None:
        self._password_hasher = password_hasher

    def create_user(
        self,
        user_id: UserId,
        username: Username,
        password_hash: UserPasswordHash,
        *,
        now: UtcDatetime,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        if role.is_system:
            raise RoleAssignmentNotPermittedError
        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
            created_at=now,
            updated_at=now,
        )

    async def create_user_with_raw_password(
        self,
        user_id: UserId,
        username: Username,
        raw_password: RawPassword,
        *,
        now: UtcDatetime,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        password_hash = await self._password_hasher.hash(raw_password)
        return self.create_user(
            user_id,
            username,
            password_hash,
            now=now,
            role=role,
            is_active=is_active,
        )

    async def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        return await self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash,
        )

    async def change_password(
        self,
        user: User,
        raw_password: RawPassword,
        *,
        now: UtcDatetime,
    ) -> None:
        user.password_hash = await self._password_hasher.hash(raw_password)
        user.updated_at = now

    def set_role(
        self,
        user: User,
        *,
        now: UtcDatetime,
        is_admin: bool,
    ) -> bool:
        if user.role.is_system:
            raise RoleChangeNotPermittedError
        target_role = UserRole.ADMIN if is_admin else UserRole.USER
        if user.role == target_role:
            return False
        user.role = target_role
        user.updated_at = now
        return True

    def set_activation(
        self,
        user: User,
        *,
        now: UtcDatetime,
        is_active: bool,
    ) -> bool:
        if user.role.is_system:
            raise ActivationChangeNotPermittedError
        if user.is_active == is_active:
            return False
        user.is_active = is_active
        user.updated_at = now
        return True
