from dataclasses import dataclass

from app.common.b_application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True)
class GrantAdminRequest:
    username: str


@dataclass(frozen=True, slots=True)
class GrantAdminResponse:
    username: str
    status: ResponseStatusEnum
