"""
- Flat (non-nested) models are best kept anemic (without methods).
  The behavior of such models is described in the domain service.

- When working with non-flat models, such as aggregates, it makes sense
  to have rich models (with methods). The behavior of these models is
  described within the models themselves.
"""

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    ActivationChangeNotPermitted,
    RoleChangeNotPermitted,
)
from app.domain.ports.password_hasher import PasswordHasher
from app.domain.ports.user_id_generator import UserIdGenerator
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.user_password_hash import UserPasswordHash
from app.domain.value_objects.username.username import Username


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
        user_id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))
        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=UserRole.USER,
            is_active=True,
        )

    def is_password_valid(self, user: User, raw_password: RawPassword) -> bool:
        return self._password_hasher.verify(
            raw_password=raw_password,
            hashed_password=user.password_hash.value,
        )

    def change_password(self, user: User, raw_password: RawPassword) -> None:
        hashed_password = UserPasswordHash(self._password_hasher.hash(raw_password))
        user.password_hash = hashed_password

    def toggle_user_activation(self, user: User, *, is_active: bool) -> None:
        """
        :raises ActivationChangeNotPermitted:
        """
        if user.role == UserRole.SUPER_ADMIN:
            raise ActivationChangeNotPermitted(user.username, user.role)
        user.is_active = is_active

    def toggle_user_admin_role(self, user: User, *, is_admin: bool) -> None:
        """
        :raises RoleChangeNotPermitted:
        """
        if user.role == UserRole.SUPER_ADMIN:
            raise RoleChangeNotPermitted(user.username, user.role)
        user.role = UserRole.ADMIN if is_admin else UserRole.USER
