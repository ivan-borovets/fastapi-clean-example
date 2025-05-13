# pylint: disable=C0301 (line-too-long)
import logging
from dataclasses import dataclass
from typing import TypedDict

from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user import UserNotFoundByUsername
from app.domain.services.user import UserService
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.auth_context.common.application_adapters.auth_session_identity_provider import (
    AuthSessionIdentityProvider,
)
from app.infrastructure.auth_context.common.auth_exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.auth_context.common.managers.auth_session import (
    AuthSessionManager,
)
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.auth_context.common.sqla_auth_transaction_manager import (
    SqlaAuthTransactionManager,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInRequest:
    username: str
    password: str


class LogInResponse(TypedDict):
    message: str


class LogInHandler:
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataMapperError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        auth_session_identity_provider: AuthSessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        auth_session_manager: AuthSessionManager,
        jtw_token_manager: JwtTokenManager,
        user_service: UserService,
        sqla_auth_transaction_manager: SqlaAuthTransactionManager,
    ):
        self._auth_session_identity_provider = auth_session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._auth_session_manager = auth_session_manager
        self._jwt_token_manager = jtw_token_manager
        self._user_service = user_service
        self._sqla_auth_transaction_manager = sqla_auth_transaction_manager

    async def __call__(self, request_data: LogInRequest) -> LogInResponse:
        log.info("Log in: started. Username: '%s'.", request_data.username)

        try:
            await self._auth_session_identity_provider.get_current_user_id()
            raise AlreadyAuthenticatedError(
                "You are already authenticated. Consider logging out."
            )
        except AuthenticationError:
            pass

        username = Username(request_data.username)
        password = RawPassword(request_data.password)

        user: User | None = await self._sqla_user_data_mapper.read_by_username(username)
        if user is None:
            raise UserNotFoundByUsername(username)

        if not self._user_service.is_password_valid(user, password):
            raise AuthenticationError("Invalid password.")

        if not user.is_active:
            raise AuthenticationError(
                "Your account is inactive. Please contact support."
            )

        auth_session: AuthSession = (
            await self._auth_session_manager.create_auth_session(user.id_)
        )
        if not await self._auth_session_manager.add_auth_session(auth_session):
            raise AuthenticationError(
                "Authentication is currently unavailable. Please try again later."
            )

        access_token: str = self._jwt_token_manager.issue_access_token(auth_session.id_)
        self._jwt_token_manager.add_access_token_to_request(access_token)

        await self._sqla_auth_transaction_manager.commit()

        log.info(
            "Log in: done. User, id: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )
        return LogInResponse(message="Logged in: successful.")
