"""
Sentinel for "value was not provided", as opposed to `None` ("provided as empty").
Single-member `Enum`: type checkers narrow `is` only for enum members, `None` and literals.
"""

from collections.abc import Callable
from enum import Enum
from typing import Final, overload


class Omitted(Enum):
    OMITTED = "OMITTED"


OMITTED: Final = Omitted.OMITTED


@overload
def apply_when_present[T, R](func: Callable[[T], R], value: T | Omitted) -> R | Omitted: ...
@overload
def apply_when_present[T, R](func: Callable[[T], R], value: T | None | Omitted) -> R | None | Omitted: ...
def apply_when_present[T, R](func: Callable[[T], R], value: T | None | Omitted) -> R | None | Omitted:
    if value is OMITTED:
        return OMITTED
    if value is None:
        return None
    return func(value)
