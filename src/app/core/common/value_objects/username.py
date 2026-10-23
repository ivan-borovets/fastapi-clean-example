import re
from dataclasses import dataclass
from typing import ClassVar

from app.core.common.exceptions import BusinessTypeError
from app.core.common.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):
    MIN_LEN: ClassVar[int] = 5
    MAX_LEN: ClassVar[int] = 20

    # 1) allowed alphabet only
    PATTERN_ALLOWED_CHARS: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9._-]+$")
    # 2) start / end must be alnum
    PATTERN_START: ClassVar[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9]")
    PATTERN_END: ClassVar[re.Pattern[str]] = re.compile(r"[A-Za-z0-9]$")
    # 3) no consecutive specials
    PATTERN_CONSECUTIVE_SPECIALS: ClassVar[re.Pattern[str]] = re.compile(r"[._-]{2,}")

    value: str

    def __post_init__(self) -> None:
        self._validate(self.value)

    @classmethod
    def _validate(cls, value: str) -> None:
        if len(value) < cls.MIN_LEN or len(value) > cls.MAX_LEN:
            raise BusinessTypeError(f"{cls.__name__} must be between {cls.MIN_LEN} and {cls.MAX_LEN} characters.")
        if not cls.PATTERN_ALLOWED_CHARS.fullmatch(value):
            raise BusinessTypeError(
                f"{cls.__name__} can only contain letters (A-Z, a-z), digits (0-9), "
                "dots (.), hyphens (-), and underscores (_)."
            )
        if not cls.PATTERN_START.match(value):
            raise BusinessTypeError(f"{cls.__name__} must start with a letter (A-Z, a-z) or a digit (0-9).")
        if not cls.PATTERN_END.search(value):
            raise BusinessTypeError(f"{cls.__name__} must end with a letter (A-Z, a-z) or a digit (0-9).")
        if cls.PATTERN_CONSECUTIVE_SPECIALS.search(value):
            raise BusinessTypeError(f"{cls.__name__} cannot contain consecutive special characters like .., --, or __.")
