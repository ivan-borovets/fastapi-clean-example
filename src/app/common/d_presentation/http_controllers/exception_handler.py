import logging
from dataclasses import dataclass
from typing import Any

import pydantic
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from pydantic_core import ErrorDetails

from app.base.a_domain.exceptions import DomainError
from app.base.b_application.exceptions import ApplicationError
from app.distinct.user.a_domain.exceptions.existence import UsernameAlreadyExists
from app.distinct.user.a_domain.exceptions.expiration import SessionExpired
from app.distinct.user.a_domain.exceptions.non_existence import (
    SessionNotFoundById,
    UserNotFoundById,
    UserNotFoundByUsername,
)
from app.distinct.user.b_application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExceptionSchema:
    description: str


@dataclass(frozen=True, slots=True)
class ExceptionSchemaRich:
    description: str
    details: list[dict[str, Any]] | None = None


class ExceptionMessageProvider:
    @staticmethod
    def get_exception_message(exc: Exception, status_code: int) -> str:
        return "Internal server error." if status_code == 500 else str(exc)


class ExceptionMapper:
    def __init__(self) -> None:
        self.exceptions_status_code_map: dict[type[Exception], int] = {
            pydantic.ValidationError: status.HTTP_400_BAD_REQUEST,
            AuthenticationError: status.HTTP_401_UNAUTHORIZED,
            SessionExpired: status.HTTP_401_UNAUTHORIZED,
            AuthorizationError: status.HTTP_403_FORBIDDEN,
            SessionNotFoundById: status.HTTP_404_NOT_FOUND,
            UserNotFoundById: status.HTTP_404_NOT_FOUND,
            UserNotFoundByUsername: status.HTTP_404_NOT_FOUND,
            UsernameAlreadyExists: status.HTTP_409_CONFLICT,
            DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    def get_status_code(self, exc: Exception) -> int:
        return self.exceptions_status_code_map.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExceptionHandler:
    def __init__(
        self,
        app: FastAPI,
        exception_message_provider: ExceptionMessageProvider,
        exception_mapper: ExceptionMapper,
    ):
        self._app = app
        self._mapper = exception_mapper
        self._exception_message_provider = exception_message_provider

    def setup_handlers(self) -> None:
        for exc_class in self._mapper.exceptions_status_code_map:
            self._app.add_exception_handler(exc_class, self._handle_exception)
        self._app.add_exception_handler(Exception, self._handle_unexpected_exceptions)

    async def _handle_exception(self, _: Request, exc: Exception) -> ORJSONResponse:
        status_code: int = self._mapper.get_status_code(exc)

        if status_code >= 500:
            log.error(
                "Exception %s occurred: %s",
                type(exc).__name__,
                exc,
                exc_info=True,
            )
        else:
            log.warning(
                "Exception %s occurred: %s",
                type(exc).__name__,
                exc,
            )

        exception_message: str = self._exception_message_provider.get_exception_message(
            exc, status_code
        )

        details: list[ErrorDetails] | None = (
            exc.errors() if isinstance(exc, pydantic.ValidationError) else None
        )

        return self._create_exception_response(status_code, exception_message, details)

    async def _handle_unexpected_exceptions(
        self, _: Request, exc: Exception
    ) -> ORJSONResponse:
        log.error(
            "Unexpected exception %s occurred: %s",
            type(exc).__name__,
            exc,
            exc_info=True,
        )
        exception_message: str = "Internal server error."
        return self._create_exception_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR, exception_message
        )

    @staticmethod
    def _create_exception_response(
        status_code: int,
        exception_message: str,
        details: list[ErrorDetails] | None = None,
    ) -> ORJSONResponse:
        response_content: ExceptionSchemaRich | ExceptionSchema = (
            ExceptionSchemaRich(exception_message, jsonable_encoder(details))
            if details
            else ExceptionSchema(exception_message)
        )
        return ORJSONResponse(status_code=status_code, content=response_content)
