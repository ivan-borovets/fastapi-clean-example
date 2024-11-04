import logging

from app.application.exceptions import AdapterError, DataGatewayError
from app.application.user.exceptions import AuthenticationError, SessionExpired
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.protocols.account_user_service import AccountUserService
from app.application.user.record_session import SessionRecord
from app.application.user.services.authentication import AuthenticationService
from app.application.user.services.session import SessionService
from app.application.user.services.token import TokenService
from app.domain.user.entity_user import User
from app.domain.user.exceptions.non_existence import (
    SessionNotFoundById,
    UserNotFoundById,
)
from app.domain.user.vo_user import UserId, Username

log = logging.getLogger(__name__)


class AccountService:
    def __init__(
        self,
        account_user_service: AccountUserService,
        authentication_service: AuthenticationService,
        session_service: SessionService,
        token_service: TokenService,
        identity_provider: IdentityProvider,
    ):
        self._account_user_service = account_user_service
        self._authentication_service = authentication_service
        self._session_service = session_service
        self._token_service = token_service
        self._identity_provider = identity_provider

    async def sign_up(self, username: Username, password: str) -> None:
        """
        :raises AuthenticationError:
        :raises DataGatewayError:
        :raises UsernameAlreadyExists:
        """
        log.info("Sign up: started. Username: '%s'.", username.value)

        if await self._authentication_service.is_authenticated():
            raise AuthenticationError(
                "You are already authenticated. Consider logging out."
            )

        await self._account_user_service.check_username_uniqueness(username)

        user: User = await self._account_user_service.create_user(username, password)
        await self._account_user_service.save_user(user)

        log.info("Sign up: done. Username: '%s'.", username.value)

    async def log_in(self, username: Username, password: str) -> None:
        """
        :raises AuthenticationError:
        :raises DataGatewayError:
        :raises UserNotFoundByUsername:
        """
        log.info("Log in: started. Username: '%s'.", username.value)

        if await self._authentication_service.is_authenticated():
            raise AuthenticationError(
                "You are already authenticated. Consider logging out."
            )

        user: User = await self._account_user_service.get_user_by_username(username)
        self._authentication_service.authenticate(user, password)

        session: SessionRecord = await self._session_service.create_session(user.id_)
        await self._session_service.save_session(session)

        access_token: str = self._token_service.issue_access_token(session.id_)
        self._token_service.add_access_token_to_request(access_token)

        log.info(
            "Log in: done. User, id: '%s', username '%s', roles '%s'.",
            user.id_.value,
            user.username.value,
            ", ".join(str(role.value) for role in user.roles),
        )

    async def log_out(self) -> None:
        """
        :raises AuthenticationError:
        :raises DataGatewayError:
        """
        log.info("Log out: started for unknown user.")
        try:
            user_id: UserId = await self._identity_provider.get_current_user_id()
        except (
            AdapterError,
            SessionNotFoundById,
            DataGatewayError,
            SessionExpired,
        ) as error:
            log.error("User id retrieving failed: '%s'", error)
            raise AuthenticationError("Not authenticated.") from error

        try:
            user: User = await self._account_user_service.get_user_by_id(user_id)
        except (
            DataGatewayError,
            UserNotFoundById,
        ) as error:
            log.error("User retrieving failed: '%s'", error)
            raise AuthenticationError("Not authenticated.") from error

        log.info("Log out: user identified. Username: '%s'.", user.username.value)

        try:
            session: SessionRecord = await self._session_service.get_current_session()
        except (
            AdapterError,
            DataGatewayError,
            SessionNotFoundById,
            SessionExpired,
        ) as error:
            log.error("Session retrieving failed: '%s'", error)
            raise AuthenticationError("Not authenticated.") from error

        self._token_service.delete_access_token_from_request()
        log.debug("Access token deleted. Session id: '%s'.", session.id_)

        try:
            await self._session_service.delete_session(session.id_)
            log.debug("Session deleted. Session id: '%s'.", session.id_)
        except (
            DataGatewayError,
            SessionNotFoundById,
        ) as error:
            log.error("Session deletion failed: '%s'", error)
            raise DataGatewayError("Session deletion failed.") from error

        log.info("Log out: done. Username: '%s'.", user.username.value)
