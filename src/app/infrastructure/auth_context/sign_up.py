# pylint: disable=C0301 (line-too-long)
import logging
from dataclasses import dataclass
from typing import TypedDict

from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user import UsernameAlreadyExists
from app.domain.services.user import UserService
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.adapters.application.sqla_user_transaction_manager import (
    SqlaUserTransactionManager,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_context.common.auth_exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpRequest:
    username: str
    password: str


class SignUpResponse(TypedDict):
    username: str
    status: ResponseStatusEnum


class SignUpHandler:
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataMapperError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        user_service: UserService,
        sqla_user_transaction_manager: SqlaUserTransactionManager,
    ):
        self._auth_session_identity_provider = auth_session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._user_service = user_service
        self._sqla_user_transaction_manager = sqla_user_transaction_manager

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._auth_session_identity_provider.get_current_user_id()
            raise AlreadyAuthenticatedError(
                "You are already authenticated. Consider logging out."
            )
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user: User = self._user_service.create_user(username, password)

        await self._sqla_user_data_mapper.add(user)

        try:
            await self._sqla_user_transaction_manager.flush()
        except UsernameAlreadyExists:
            raise

        await self._sqla_user_transaction_manager.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(
            username=user.username.value,
            status=ResponseStatusEnum.CREATED,
        )
