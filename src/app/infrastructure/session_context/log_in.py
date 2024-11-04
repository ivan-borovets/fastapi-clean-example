# pylint: disable=C0301 (line-too-long)
import logging
from dataclasses import dataclass

from app.domain.user.entity import User
from app.domain.user.exceptions.non_existence import UserNotFoundByUsername
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.session_context.common.application_adapters.session_identity_provider import (
    SessionIdentityProvider,
)
from app.infrastructure.session_context.common.authentication_exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.session_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.session_context.common.managers.session import SessionManager
from app.infrastructure.session_context.common.session_record import SessionRecord

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class LogInRequest:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class LogInResponse:
    message: str


class LogInInteractor:
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataMapperError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        session_manager: SessionManager,
        jtw_token_manager: JwtTokenManager,
        user_service: UserService,
    ):
        self._session_identity_provider = session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._session_manager = session_manager
        self._jwt_token_manager = jtw_token_manager
        self._user_service = user_service

    async def __call__(self, request_data: LogInRequest) -> LogInResponse:
        log.info("Log in: started. Username: '%s'.", request_data.username)

        try:
            await self._session_identity_provider.get_current_user_id()
            raise AlreadyAuthenticatedError(
                "You are already authenticated. Consider logging out."
            )
        except AuthenticationError:
            pass

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        user: User | None = await self._sqla_user_data_mapper.read_by_username(username)
        if user is None:
            raise UserNotFoundByUsername(username)

        if not self._user_service.is_password_valid(user, password):
            raise AuthenticationError("Invalid password.")

        if not user.is_active:
            raise AuthenticationError(
                "Your account is inactive. Please contact support."
            )

        session: SessionRecord = await self._session_manager.create_session(user.id_)
        if not await self._session_manager.save_session(session):
            raise AuthenticationError(
                "Authentication is currently unavailable. Please try again later."
            )

        access_token: str = self._jwt_token_manager.issue_access_token(session.id_)
        self._jwt_token_manager.add_access_token_to_request(access_token)

        log.info(
            "Log in: done. User, id: '%s', username '%s', role '%s'.",
            user.id_.value,
            user.username.value,
            user.role.value,
        )
        return LogInResponse("Logged in: successful.")
