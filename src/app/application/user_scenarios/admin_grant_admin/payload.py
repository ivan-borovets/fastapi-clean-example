from dataclasses import dataclass

from app.application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class GrantAdminRequest:
    username: str


@dataclass(frozen=True, slots=True)
class GrantAdminResponse:
    username: str
    status: ResponseStatusEnum
