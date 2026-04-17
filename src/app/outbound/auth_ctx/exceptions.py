from typing import ClassVar

from app.core.common.exceptions import BaseError


class AuthenticationError(BaseError):
    default_message: ClassVar[str] = "Not authenticated."


class AlreadyAuthenticatedError(BaseError):
    default_message: ClassVar[str] = "You are already authenticated. Consider logging out."


class ReAuthenticationError(BaseError):
    default_message: ClassVar[str] = "Invalid password."


class AuthenticationChangeError(BaseError):
    default_message: ClassVar[str] = "New password must differ from current password."
