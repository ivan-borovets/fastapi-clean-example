from typing import Any, Final

from fastapi_error_map import StructuredErrorResponse
from starlette import status

type OpenApiResponses = dict[int | str, dict[str, Any]]

SERVER_ERROR_RESPONSES: Final[OpenApiResponses] = {
    status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": StructuredErrorResponse},
}
