from dataclasses import dataclass

from app.application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class InactivateUserRequest:
    username: str


@dataclass(frozen=True, slots=True)
class InactivateUserResponse:
    username: str
    status: ResponseStatusEnum
