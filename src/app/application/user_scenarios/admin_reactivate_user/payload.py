from dataclasses import dataclass

from app.application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class ReactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class ReactivateUserResponse:
    username: str
    status: ResponseStatusEnum
