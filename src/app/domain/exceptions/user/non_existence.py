from app.domain.entities.user.value_objects import UserId, Username
from app.domain.exceptions.base import DomainError


class UserNotFoundById(DomainError):
    def __init__(self, user_id: UserId):
        message: str = f"User with id '{user_id.value}' is not found."
        super().__init__(message)


class UserNotFoundByUsername(DomainError):
    def __init__(self, username: Username):
        message: str = f"User with username '{username.value}' is not found."
        super().__init__(message)
