import re
from dataclasses import dataclass
from typing import ClassVar, Final

from app.domain.exceptions.base import DomainTypeError
from app.domain.value_objects.base import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class Username(ValueObject):
    """raises DomainTypeError"""

    MIN_LEN: ClassVar[Final[int]] = 5
    MAX_LEN: ClassVar[Final[int]] = 20

    # Pattern for validating a username:
    # - starts with a letter (A-Z, a-z) or a digit (0-9)
    PATTERN_START: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]",
    )
    # - can contain multiple special characters . - _ between letters and digits,
    PATTERN_ALLOWED_CHARS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"[a-zA-Z0-9._-]*",
    )
    #   but only one special character can appear consecutively
    PATTERN_NO_CONSECUTIVE_SPECIALS: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[a-zA-Z0-9]+([._-]?[a-zA-Z0-9]+)*[._-]?$",
    )
    # - ends with a letter (A-Z, a-z) or a digit (0-9)
    PATTERN_END: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r".*[a-zA-Z0-9]$",
    )

    value: str

    def __post_init__(self) -> None:
        """:raises DomainTypeError:"""
        self._validate_username_length(self.value)
        self._validate_username_pattern(self.value)

    def _validate_username_length(self, username_value: str) -> None:
        """:raises DomainTypeError:"""
        if len(username_value) < self.MIN_LEN or len(username_value) > self.MAX_LEN:
            raise DomainTypeError(
                f"Username must be between "
                f"{self.MIN_LEN} and "
                f"{self.MAX_LEN} characters.",
            )

    def _validate_username_pattern(self, username_value: str) -> None:
        """:raises DomainTypeError:"""
        if not re.match(self.PATTERN_START, username_value):
            raise DomainTypeError(
                "Username must start with a letter (A-Z, a-z) or a digit (0-9).",
            )
        if not re.fullmatch(self.PATTERN_ALLOWED_CHARS, username_value):
            raise DomainTypeError(
                "Username can only contain letters (A-Z, a-z), digits (0-9), "
                "dots (.), hyphens (-), and underscores (_).",
            )
        if not re.fullmatch(self.PATTERN_NO_CONSECUTIVE_SPECIALS, username_value):
            raise DomainTypeError(
                "Username cannot contain consecutive special characters"
                " like .., --, or __.",
            )
        if not re.match(self.PATTERN_END, username_value):
            raise DomainTypeError(
                "Username must end with a letter (A-Z, a-z) or a digit (0-9).",
            )
