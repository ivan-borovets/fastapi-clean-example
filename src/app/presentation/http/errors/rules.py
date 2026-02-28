from typing import Final

from fastapi_error_map.rules import Rule, rule
from starlette import status

from app.presentation.http.errors.translators import ServiceUnavailableTranslator

HTTP_503_SERVICE_UNAVAILABLE_RULE: Final[Rule] = rule(
    status=status.HTTP_503_SERVICE_UNAVAILABLE,
    translator=ServiceUnavailableTranslator(),
)
