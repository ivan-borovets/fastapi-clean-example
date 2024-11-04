"""
- Flat (non-nested) models are best kept anemic (without methods).
  The behavior of such models is described in the domain service.

- When working with non-flat models, such as aggregates, it makes sense
  to have rich models (with methods). The behavior of these models is
  described within the models themselves.
"""

from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import (
    RawPassword,
    UserId,
    Username,
    UserPasswordHash,
)
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator


class UserService:
    def __init__(
        self,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher

    def create_user(self, username: Username, raw_password: RawPassword) -> User:
        """
        :raises DomainFieldError:
        """
        user_id: UserId = UserId(self._user_id_generator())
        password_hash: UserPasswordHash = UserPasswordHash(
            self._password_hasher.hash(raw_password)
        )

        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=UserRoleEnum.USER,
            is_active=True,
        )

    def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash.value,
        )

    def change_password(self, user: User, raw_password: RawPassword) -> None:
        hashed_password: UserPasswordHash = UserPasswordHash(
            self._password_hasher.hash(raw_password)
        )
        user.password_hash = hashed_password

    def toggle_user_activation(self, user: User, is_active: bool) -> None:
        user.is_active = is_active

    def toggle_user_admin_role(self, user: User, is_admin: bool) -> None:
        user.role = UserRoleEnum.ADMIN if is_admin else UserRoleEnum.USER
