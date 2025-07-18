from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

import pydantic
from starlette import status

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.exceptions.base import ApplicationError
from app.application.common.exceptions.query import SortingError
from app.domain.exceptions.base import DomainError, DomainFieldError
from app.domain.exceptions.user import (
    ActivationChangeNotPermittedError,
    RoleAssignmentNotPermittedError,
    RoleChangeNotPermittedError,
    UsernameAlreadyExistsError,
    UserNotFoundByUsernameError,
)
from app.infrastructure.auth.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.exceptions.base import InfrastructureError
from app.infrastructure.exceptions.gateway import DataMapperError, ReaderError

MSG_INTERNAL_SERVER_ERROR: Final[str] = "Internal server error."
MSG_SERVICE_UNAVAILABLE: Final[str] = (
    "Service temporarily unavailable. Please try again later."
)

ERROR_STATUS_MAPPING: Final[Mapping[type[Exception], int]] = MappingProxyType({
    # 400
    DomainFieldError: status.HTTP_400_BAD_REQUEST,
    SortingError: status.HTTP_400_BAD_REQUEST,
    # 401
    AlreadyAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    # 403
    ActivationChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    RoleChangeNotPermittedError: status.HTTP_403_FORBIDDEN,
    # 404
    UserNotFoundByUsernameError: status.HTTP_404_NOT_FOUND,
    # 409
    UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
    # 422
    pydantic.ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    RoleAssignmentNotPermittedError: status.HTTP_422_UNPROCESSABLE_ENTITY,
    # 500
    ApplicationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    DomainError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    InfrastructureError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    # 503
    DataMapperError: status.HTTP_503_SERVICE_UNAVAILABLE,
    ReaderError: status.HTTP_503_SERVICE_UNAVAILABLE,
})
