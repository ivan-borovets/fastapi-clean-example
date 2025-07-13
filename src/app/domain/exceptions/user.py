from typing import Any

from app.domain.enums.user_role import UserRole
from app.domain.exceptions.base import DomainError
from app.domain.value_objects.username.username import Username


class UsernameAlreadyExistsError(DomainError):
    def __init__(self, username: Any):
        message = f"User with username {username!r} already exists."
        super().__init__(message)


class UserNotFoundByUsernameError(DomainError):
    def __init__(self, username: Username):
        message = f"User with username {username.value!r} is not found."
        super().__init__(message)


class ActivationChangeNotPermittedError(DomainError):
    def __init__(self, username: Username, role: UserRole):
        message = (
            f"Changing activation of user {username.value!r} ({role}) is not permitted."
        )
        super().__init__(message)


class RoleAssignmentNotPermittedError(DomainError):
    def __init__(self, role: UserRole):
        message = f"Assignment of role {role} is not permitted."
        super().__init__(message)


class RoleChangeNotPermittedError(DomainError):
    def __init__(self, username: Username, role: UserRole):
        message = f"Changing role of user {username.value!r} ({role}) is not permitted."
        super().__init__(message)
