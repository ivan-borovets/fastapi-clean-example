import logging
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Final

import pydantic
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.exceptions.base import ApplicationError
from app.application.common.exceptions.query import SortingError
from app.domain.exceptions.base import DomainError, DomainFieldError
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    RoleChangeNotPermittedError,
    UsernameAlreadyExistsError,
    UserNotFoundByUsernameError,
)
from app.infrastructure.exceptions.authentication import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.exceptions.base import InfrastructureError
from app.infrastructure.exceptions.gateway import DataMapperError, ReaderError

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionHandler:
    _ERROR_MAPPING: Final[MappingProxyType[type[Exception], int]] = MappingProxyType({
        # 400
        DomainFieldError: status.HTTP_400_BAD_REQUEST,
        SortingError: status.HTTP_400_BAD_REQUEST,
        # 401
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AlreadyAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
        # 403
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        ActivationChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
        # 404
        UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
        # 409
        UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        # 422
        pydantic.ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        # 500
        DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        InfrastructureError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        # 503
        DataMapperError: status.HTTP_503_SERVICE_UNAVAILABLE,
        ReaderError: status.HTTP_503_SERVICE_UNAVAILABLE,
    })

    def __init__(self, app: FastAPI):
        self._app = app

    async def _handle(self, _: Request, exc: Exception) -> ORJSONResponse:
        status_code: int = self._ERROR_MAPPING.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        response: ExceptionSchema | ExceptionSchemaRich
        if isinstance(exc, pydantic.ValidationError):
            message = str(exc)
            response = ExceptionSchemaRich(message, jsonable_encoder(exc.errors()))

        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            message = "Service temporarily unavailable. Please try again later."
            response = ExceptionSchema(message)

        else:
            message = str(exc) if status_code < 500 else "Internal server error."
            response = ExceptionSchema(message)

        if status_code >= 500:
            log.error(
                "Exception '%s' occurred: '%s'.",
                type(exc).__name__,
                exc,
                exc_info=exc,
            )

        else:
            log.warning("Exception '%s' occurred: '%s'.", type(exc).__name__, exc)

        return ORJSONResponse(
            status_code=status_code,
            content=response,
        )

    def setup_handlers(self) -> None:
        for exc_class in self._ERROR_MAPPING:
            self._app.add_exception_handler(exc_class, self._handle)
        self._app.add_exception_handler(Exception, self._handle)
