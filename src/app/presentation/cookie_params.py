from dataclasses import dataclass
from typing import Literal


@dataclass(eq=False, slots=True, kw_only=True)
class CookieParams:
    secure: bool
    samesite: Literal["strict"] | None = None
