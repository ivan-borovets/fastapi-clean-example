from dataclasses import dataclass

from app.common.b_application.enums import ResponseStatusEnum


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpRequest:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class SignUpResponse:
    username: str
    status: ResponseStatusEnum
