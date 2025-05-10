from typing import Any

from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import UserId, Username
from app.domain.exceptions.base import DomainError


class UsernameAlreadyExists(DomainError):
    def __init__(self, username: Any):
        message = f"User with username '{username}' already exists."
        super().__init__(message)


class UserNotFoundById(DomainError):
    def __init__(self, user_id: UserId):
        message = f"User with id '{user_id.value}' is not found."
        super().__init__(message)


class UserNotFoundByUsername(DomainError):
    def __init__(self, username: Username):
        message = f"User with username '{username.value}' is not found."
        super().__init__(message)


class ActivationChangeNotPermitted(DomainError):
    def __init__(self, username: Username, role: UserRoleEnum):
        message = (
            f"Changing activation of user '{username.value}' ({role}) is not permitted."
        )
        super().__init__(message)


class RoleChangeNotPermitted(DomainError):
    def __init__(self, username: Username, role: UserRoleEnum):
        message = f"Changing role of user '{username.value}' ({role}) is not permitted."
        super().__init__(message)
