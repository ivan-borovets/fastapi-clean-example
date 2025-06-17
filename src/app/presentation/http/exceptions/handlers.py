__all__ = ("setup_handlers",)

import logging
from typing import Any, cast

import pydantic
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.requests import Request

from app.presentation.http.exceptions.constants import (
    ERROR_STATUS_MAPPING,
    MSG_INTERNAL_SERVER_ERROR,
    MSG_SERVICE_UNAVAILABLE,
)
from app.presentation.http.exceptions.schemas import (
    ExceptionSchema,
    ExceptionSchemaDetailed,
)

log = logging.getLogger(__name__)


def setup_handlers(app: FastAPI) -> None:
    for exc_class in ERROR_STATUS_MAPPING:
        app.add_exception_handler(exc_class, handle_exception)
    app.add_exception_handler(Exception, handle_exception)


async def handle_exception(_: Request, exc: Exception) -> ORJSONResponse:
    status_code = resolve_status_code(exc)
    response = build_exception_response(exc, status_code)
    log_exception(exc, status_code)
    return ORJSONResponse(status_code=status_code, content=jsonable_encoder(response))


def resolve_status_code(exc: Exception) -> int:
    return ERROR_STATUS_MAPPING.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def build_exception_response(exc: Exception, status_code: int) -> ExceptionSchema:
    if isinstance(exc, pydantic.ValidationError):
        return ExceptionSchemaDetailed(
            description=str(exc),
            details=cast(list[dict[str, Any]], exc.errors()),
        )

    if status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
        return ExceptionSchema(MSG_SERVICE_UNAVAILABLE)

    description = (
        str(exc)
        if status_code < status.HTTP_500_INTERNAL_SERVER_ERROR
        else MSG_INTERNAL_SERVER_ERROR
    )
    return ExceptionSchema(description)


def log_exception(exc: Exception, status_code: int) -> None:
    is_server_error = status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR
    log_func = log.error if is_server_error else log.warning

    log_func(
        "Exception '%s' occurred: '%s'.",
        type(exc).__name__,
        exc,
        exc_info=exc if is_server_error else None,
    )
