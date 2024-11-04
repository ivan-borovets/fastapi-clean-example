import logging

from app.application.user.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.domain.user.entity import User
from app.domain.user.exceptions.non_existence import UserNotFoundByUsername
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username
from app.infrastructure.base.interactors import InteractorStrict
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.scenarios.log_in.payload import (
    LogInRequest,
    LogInResponse,
)
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.services.session import SessionService
from app.infrastructure.user.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.user.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)

log = logging.getLogger(__name__)


class LogInInteractor(InteractorStrict[LogInRequest, LogInResponse]):
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataGatewayError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        session_service: SessionService,
        jtw_token_service: JwtTokenService,
        user_service: UserService,
    ):
        self._session_identity_provider = session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._session_service = session_service
        self._jwt_token_service = jtw_token_service
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

        session: SessionRecord = await self._session_service.create_session(user.id_)
        await self._session_service.save_session(session)

        access_token: str = self._jwt_token_service.issue_access_token(session.id_)
        self._jwt_token_service.add_access_token_to_request(access_token)

        log.info(
            "Log in: done. User, id: '%s', username '%s', roles '%s'.",
            user.id_.value,
            user.username.value,
            ", ".join(str(role.value) for role in user.roles),
        )
        return LogInResponse("Logged in: successful.")
