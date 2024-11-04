from dataclasses import dataclass

from app.common.b_application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class ReactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class ReactivateUserResponse:
    username: str
    status: ResponseStatusEnum
