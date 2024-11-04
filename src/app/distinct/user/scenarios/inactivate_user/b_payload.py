from dataclasses import dataclass

from app.common.b_application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class InactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class InactivateUserResponse:
    username: str
    status: ResponseStatusEnum
