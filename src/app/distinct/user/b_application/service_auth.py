import logging
from datetime import datetime, timedelta
from uuid import UUID

from app.common.b_application.exceptions import AdapterError, GatewayError
from app.common.b_application.persistence.committer import Committer
from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.exceptions.existence import UsernameAlreadyExists
from app.distinct.user.a_domain.exceptions.expiration import SessionExpired
from app.distinct.user.a_domain.exceptions.non_existence import (
    SessionNotFoundById,
    UserNotFoundById,
    UserNotFoundByUsername,
)
from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.a_domain.vo_user import UserId, Username
from app.distinct.user.b_application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.distinct.user.b_application.gateways.session import SessionGateway
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.ports.access_token_processor import (
    AccessTokenProcessor,
)
from app.distinct.user.b_application.ports.access_token_request_handler import (
    AccessTokenRequestHandler,
)
from app.distinct.user.b_application.ports.identity_provider import IdentityProvider
from app.distinct.user.b_application.ports.password_hasher import PasswordHasher
from app.distinct.user.b_application.ports.session_id_generator import (
    SessionIdGenerator,
)
from app.distinct.user.b_application.ports.session_timer import SessionTimer
from app.distinct.user.b_application.ports.user_id_generator import UserIdGenerator

log = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_gateway: UserGateway,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
        committer: Committer,
        identity_provider: IdentityProvider,
        session_id_generator: SessionIdGenerator,
        session_timer: SessionTimer,
        session_gateway: SessionGateway,
        access_token_processor: AccessTokenProcessor,
        access_token_handler: AccessTokenRequestHandler,
    ):
        self._user_gateway = user_gateway
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher
        self._committer = committer
        self._identity_provider = identity_provider
        self._session_id_generator = session_id_generator
        self._session_timer = session_timer
        self._session_gateway = session_gateway
        self._access_token_processor = access_token_processor
        self._access_token_handler = access_token_handler

    async def sign_up(self, username: Username, password: str) -> None:
        """
        :raises GatewayError:
        :raises UsernameAlreadyExists:
        """
        log.info("Sign up: '%s'.", username.value)
        log.debug("Checking username '%s' uniqueness.", username.value)
        try:
            if not await self._user_gateway.is_username_unique(username):
                raise UsernameAlreadyExists(username.value)
        except GatewayError:
            raise

        log.debug("Creating user: '%s'", username.value)
        user_id: UUID = self._user_id_generator()
        password_hash: bytes = self._password_hasher.hash(password)
        user: User = User.create(
            user_id=user_id,
            username=username.value,
            password_hash=password_hash,
        )

        log.debug("Saving user: '%s', '%s'", user_id, username.value)
        try:
            await self._user_gateway.create(user)
            await self._committer.commit()
        except GatewayError:
            raise

        log.info(
            "New user saved: '%s', '%s', '%s'.",
            user_id,
            username.value,
            ", ".join(str(role.value) for role in user.roles),
        )

    async def _check_authentication(self) -> None:
        """
        :raises AuthenticationError:
        """
        log.info("Check current user authentication.")
        log.debug("Extracting current user id.")
        try:
            await self._identity_provider.get_current_user_id()
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ) as error:
            log.error("Authentication failed: '%s'.", error)
            raise AuthenticationError("Not authenticated.") from error

    async def _generate_and_save_session_with_access_token(
        self, user_id: UserId
    ) -> None:
        """
        :raises GatewayError:
        """
        log.debug("Starting session generation for user id '%s'.", user_id.value)
        session_id: SessionId = SessionId(self._session_id_generator())
        expiration: datetime = self._session_timer.access_expiration
        session: Session = Session.create(
            session_id=session_id.value, user_id=user_id.value, expiration=expiration
        )
        try:
            await self._session_gateway.create(session)
            await self._committer.commit()
        except GatewayError:
            raise

        log.debug(
            "Session created for user id '%s'. Session id: '%s'.",
            user_id,
            session.id_.value,
        )

        access_token: str = self._access_token_processor.issue_access_token(session.id_)
        self._access_token_handler.add_access_token_to_request(access_token)
        log.debug(
            "Access token issued and added to request for session id: '%s'.",
            session.id_.value,
        )

    async def log_in(self, username: Username, password: str) -> None:
        """
        :raises AuthenticationError:
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        log.info("Log in: '%s'.", username.value)
        log.debug("Checking whether current user is already authenticated.")
        try:
            await self._check_authentication()
        except AuthenticationError:
            pass
        else:
            raise AuthenticationError(
                "You are already authenticated. Consider logging out."
            )

        log.debug("Retrieving user: '%s'.", username.value)
        try:
            user: User = await self._user_gateway.read_by_username(username)
        except (UserNotFoundByUsername, GatewayError):
            raise

        if not user.is_active:
            raise AuthenticationError(
                "Your account is currently inactive. "
                "Please contact support for assistance."
            )

        log.debug("Verifying user's '%s' password.", username.value)
        if not self._password_hasher.verify(
            raw_password=password, hashed_password=user.password_hash.value
        ):
            raise AuthenticationError("Wrong password.")

        log.debug("Generating and saving session with access token.")
        try:
            await self._generate_and_save_session_with_access_token(user.id_)
        except GatewayError:
            raise

        log.info(
            "User, id: '%s', username '%s', roles '%s' logged in.",
            user.id_.value,
            user.username.value,
            ", ".join(str(role.value) for role in user.roles),
        )

    async def _renew_session_and_access_token(self, session_id: SessionId) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """
        log.debug("Starting session renewal for session id '%s'.", session_id.value)
        new_expiration: datetime = self._session_timer.access_expiration
        try:
            await self._session_gateway.update_expiration_by_id(
                session_id, new_expiration
            )
        except (SessionNotFoundById, GatewayError):
            raise

        try:
            await self._committer.commit()
        except GatewayError:
            raise
        log.debug("Session with id '%s' updated.", session_id)

        new_access_token: str = self._access_token_processor.issue_access_token(
            session_id
        )
        self._access_token_handler.add_access_token_to_request(new_access_token)
        log.debug(
            "New access token issued and added to request for Session Id '%s'",
            session_id,
        )

    async def _extend_session_if_near_expiry(self) -> None:
        """
        :raises AdapterError:
        :raises SessionNotFoundById:
        :raises GatewayError:
        :raises SessionExpired:
        """
        log.info("Check whether session needs extension.")
        log.debug("Extracting current session.")
        try:
            current_session: Session = (
                await self._identity_provider.get_current_session()
            )
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ):
            raise

        time_remaining: timedelta = (
            current_session.expiration.value - self._session_timer.current_time
        )
        if (
            timedelta(seconds=0)
            < time_remaining
            < self._session_timer.refresh_trigger_interval
        ):
            try:
                await self._renew_session_and_access_token(current_session.id_)
            except (SessionNotFoundById, GatewayError):
                raise

    async def _check_authentication_and_extend_session(self) -> None:
        """
        :raises AuthenticationError:
        """
        try:
            await self._check_authentication()
        except AuthenticationError:
            raise

        try:
            await self._extend_session_if_near_expiry()
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ) as error:
            log.error("Session extension failed: '%s'", error)

    async def check_authorization(self, role_required: UserRoleEnum) -> None:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        """
        log.info("Check current user authorization.")
        try:
            await self._check_authentication_and_extend_session()
        except AuthenticationError:
            raise

        try:
            current_user_roles: set[UserRoleEnum] = (
                await self._identity_provider.get_current_user_roles()
            )
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
            UserNotFoundById,
        ) as error:
            log.error("Authorization failed: '%s'.", error)
            raise AuthorizationError("Authorization failed.") from error

        if role_required not in current_user_roles:
            log.error(
                "Authorization failed. Current roles: '%s'. Required role: '%s'.",
                current_user_roles,
                role_required,
            )
            raise AuthorizationError("Not authorized.")

    async def _delete_session_and_access_token(self, session_id: SessionId) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """
        log.debug("Starting session deletion for session id '%s'.", session_id)
        try:
            await self._session_gateway.delete_by_id(session_id)
        except (SessionNotFoundById, GatewayError):
            raise

        log.debug("Deleting access token.")
        self._access_token_handler.delete_access_token_from_request()

    async def log_out(self) -> None:
        """
        :raises AuthenticationError:
        """
        try:
            user_id: UserId = await self._identity_provider.get_current_user_id()
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ) as error:
            log.error("Log out issue: '%s'.", error)
            raise AuthenticationError("Not authenticated.") from error

        try:
            user: User = await self._user_gateway.read_by_id(user_id)
        except (UserNotFoundById, GatewayError) as error:
            log.error(
                "Log out issue. User id: '%s'. Issue: '%s'.", user_id.value, error
            )
            raise AuthenticationError("Not authenticated.") from error

        log.info("Log out, user: '%s'.", user.username.value)

        log.debug("Extracting current session.")
        try:
            current_session: Session = (
                await self._identity_provider.get_current_session()
            )
        except (
            AdapterError,
            SessionNotFoundById,
            GatewayError,
            SessionExpired,
        ) as error:
            log.error(
                "Log out issue. Username: '%s'. Issue: '%s'.",
                user.username.value,
                error,
            )
            raise AuthenticationError("Not authenticated.") from error

        try:
            await self._delete_session_and_access_token(current_session.id_)
        except (SessionNotFoundById, GatewayError) as error:
            log.error(
                "Log out issue. Username: '%s'. Issue: '%s'.",
                user.username.value,
                error,
            )
            raise AuthenticationError("Not authenticated.") from error

        log.info("User '%s' logged out.", user.username.value)

    async def delete_all_sessions_by_user_id(self, user_id: UserId) -> None:
        """
        :raises GatewayError:
        """
        log.info("Deleting all sessions by user id: '%s'.", user_id.value)

        try:
            await self._session_gateway.delete_all_of_user_id(user_id)
        except GatewayError:
            raise

        log.info("All sessions for user id '%s' are deleted.", user_id.value)
