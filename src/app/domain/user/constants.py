import re

PASSWORD_MIN_LEN: int = 6

USERNAME_MIN_LEN: int = 5
USERNAME_MAX_LEN: int = 20

# Pattern for validating a username:
# - starts with a letter (A-Z, a-z) or a digit (0-9)
PATTERN_START: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9]",
)
# - can contain multiple special characters . - _ between letters and digits,
PATTERN_ALLOWED_CHARS: re.Pattern[str] = re.compile(
    r"[a-zA-Z0-9._-]*",
)
#   but only one special character can appear consecutively
PATTERN_NO_CONSECUTIVE_SPECIALS: re.Pattern[str] = re.compile(
    r"^[a-zA-Z0-9]+([._-]?[a-zA-Z0-9]+)*[._-]?$",
)
# - ends with a letter (A-Z, a-z) or a digit (0-9)
PATTERN_END: re.Pattern[str] = re.compile(
    r".*[a-zA-Z0-9]$",
)
