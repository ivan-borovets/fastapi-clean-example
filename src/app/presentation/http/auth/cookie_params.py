from dataclasses import dataclass
from typing import Literal


@dataclass(eq=False, slots=True, kw_only=True)
class CookieParams:
    secure: bool
    samesite: Literal["strict"] | None = None

    def __post_init__(self) -> None:
        if self.secure and self.samesite is None:
            self.samesite = "strict"
