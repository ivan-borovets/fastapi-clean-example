import re

from app.distinct.user.a_domain.constants import (
    PATTERN_ALLOWED_CHARS,
    PATTERN_END,
    PATTERN_NO_CONSECUTIVE_SPECIALS,
    PATTERN_START,
)


def validate_username(value: str) -> str:
    if not re.match(PATTERN_START, value):
        raise ValueError(
            "Username must start with a letter (A-Z, a-z) or a digit (0-9)."
        )
    if not re.fullmatch(PATTERN_ALLOWED_CHARS, value):
        raise ValueError(
            "Username can only contain letters (A-Z, a-z), digits (0-9), "
            "dots (.), hyphens (-), and underscores (_)."
        )
    if not re.fullmatch(PATTERN_NO_CONSECUTIVE_SPECIALS, value):
        raise ValueError(
            "Username cannot contain consecutive special characters like .., --, or __."
        )
    if not re.match(PATTERN_END, value):
        raise ValueError("Username must end with a letter (A-Z, a-z) or a digit (0-9).")
    return value
