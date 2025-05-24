import re
from typing import Final

USERNAME_MIN_LEN: Final[int] = 5
USERNAME_MAX_LEN: Final[int] = 20

# Pattern for validating a username:
# - starts with a letter (A-Z, a-z) or a digit (0-9)
PATTERN_START: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9]",
)
# - can contain multiple special characters . - _ between letters and digits,
PATTERN_ALLOWED_CHARS: Final[re.Pattern[str]] = re.compile(
    r"[a-zA-Z0-9._-]*",
)
#   but only one special character can appear consecutively
PATTERN_NO_CONSECUTIVE_SPECIALS: Final[re.Pattern[str]] = re.compile(
    r"^[a-zA-Z0-9]+([._-]?[a-zA-Z0-9]+)*[._-]?$",
)
# - ends with a letter (A-Z, a-z) or a digit (0-9)
PATTERN_END: Final[re.Pattern[str]] = re.compile(
    r".*[a-zA-Z0-9]$",
)
