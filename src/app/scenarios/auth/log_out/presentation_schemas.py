from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LogOutResponse:
    message: str
