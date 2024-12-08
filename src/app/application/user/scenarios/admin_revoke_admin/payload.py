from dataclasses import dataclass

from app.application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class RevokeAdminRequest:
    username: str


@dataclass(frozen=True, slots=True)
class RevokeAdminResponse:
    username: str
    status: ResponseStatusEnum
