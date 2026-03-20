from typing import ClassVar

from app.core.common.exceptions import BaseError


class UsernameAlreadyExistsError(BaseError):
    default_message: ClassVar[str] = "Username already exists."


class UserNotFoundError(BaseError):
    default_message: ClassVar[str] = "User not found."
