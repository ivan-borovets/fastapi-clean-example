from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
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

    def create_user(
        self,
        username: Username,
        raw_password: RawPassword,
        role: UserRole = UserRole.USER,
        is_active: bool = True,
    ) -> User:
        """
        :raises RoleAssignmentNotPermittedError:
        :raises DomainFieldError:
        """
        if not role.is_assignable:
            raise RoleAssignmentNotPermittedError(role)

        user_id = UserId(self._user_id_generator())
        password_hash = UserPasswordHash(self._password_hasher.hash(raw_password))
        return User(
            id_=user_id,
            username=username,
            password_hash=password_hash,
            role=role,
            is_active=is_active,
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
        :raises ActivationChangeNotPermittedError:
        """
        if not user.role.is_changeable:
            raise ActivationChangeNotPermittedError(user.username, user.role)
        user.is_active = is_active

    def toggle_user_admin_role(self, user: User, *, is_admin: bool) -> None:
        """
        :raises RoleChangeNotPermittedError:
        """
        if not user.role.is_changeable:
            raise RoleChangeNotPermittedError(user.username, user.role)
        user.role = UserRole.ADMIN if is_admin else UserRole.USER
