from typing import Final

from fastapi_error_map import Rule, rule, structured
from starlette import status

SERVICE_UNAVAILABLE_MESSAGE: Final[str] = "Service temporarily unavailable. Please try again later."

HTTP_503_SERVICE_UNAVAILABLE_RULE: Final[Rule] = rule(
    status=status.HTTP_503_SERVICE_UNAVAILABLE,
    translator=structured(server_message=SERVICE_UNAVAILABLE_MESSAGE)(status.HTTP_503_SERVICE_UNAVAILABLE),
)
