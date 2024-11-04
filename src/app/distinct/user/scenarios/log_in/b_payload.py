from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInRequest:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class LogInResponse:
    message: str
