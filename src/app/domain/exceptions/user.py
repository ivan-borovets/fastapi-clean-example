from typing import Any

from app.domain.enums.user_role import UserRole
from app.domain.exceptions.base import DomainError
from app.domain.value_objects.username.username import Username


class UsernameAlreadyExists(DomainError):
    def __init__(self, username: Any):
        message = f"User with username {username!r} already exists."
        super().__init__(message)


class UserNotFoundByUsername(DomainError):
    def __init__(self, username: Username):
        message = f"User with username {username.value!r} is not found."
        super().__init__(message)


class ActivationChangeNotPermitted(DomainError):
    def __init__(self, username: Username, role: UserRole):
        message = (
            f"Changing activation of user {username.value!r} ({role}) is not permitted."
        )
        super().__init__(message)


class RoleChangeNotPermitted(DomainError):
    def __init__(self, username: Username, role: UserRole):
        message = f"Changing role of user {username.value!r} ({role}) is not permitted."
        super().__init__(message)
