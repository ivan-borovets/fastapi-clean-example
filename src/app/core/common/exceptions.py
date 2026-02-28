from typing import ClassVar


class BaseError(Exception):
    default_message: ClassVar[str | None] = None

    def __init__(self, message: str | None = None) -> None:
        msg = message if message is not None else self.default_message
        super().__init__() if msg is None else super().__init__(msg)


class BusinessTypeError(BaseError):
    """Invalid construction of business logic types (Value Objects)."""


class RoleAssignmentNotPermittedError(BaseError):
    default_message: ClassVar[str] = "Assignment of role is not permitted."


class ActivationChangeNotPermittedError(BaseError):
    default_message: ClassVar[str] = "Activation change is not permitted."


class RoleChangeNotPermittedError(BaseError):
    default_message: ClassVar[str] = "Role change is not permitted."
