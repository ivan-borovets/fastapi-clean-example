from fastapi_error_map import StructuredErrorResponse, Translator, structured
from starlette import status


def internal_server_error(e: Exception) -> StructuredErrorResponse:
    translate: Translator[StructuredErrorResponse] = structured()(status.HTTP_500_INTERNAL_SERVER_ERROR)
    return translate(e)
