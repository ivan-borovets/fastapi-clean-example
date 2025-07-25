import logging
from datetime import datetime

from app.domain.value_objects.user_id import UserId
from app.infrastructure.auth.exceptions import AuthenticationError
from app.infrastructure.auth.session.constants import (
    AUTH_IS_UNAVAILABLE,
    AUTH_NOT_AUTHENTICATED,
    AUTH_SESSION_EXPIRED,
    AUTH_SESSION_EXTENSION_FAILED,
    AUTH_SESSION_EXTRACTION_FAILED,
    AUTH_SESSION_NOT_FOUND,
)
from app.infrastructure.auth.session.id_generator_str import (
    StrAuthSessionIdGenerator,
)
from app.infrastructure.auth.session.model import AuthSession
from app.infrastructure.auth.session.ports.gateway import (
    AuthSessionGateway,
)
from app.infrastructure.auth.session.ports.transaction_manager import (
    AuthSessionTransactionManager,
)
from app.infrastructure.auth.session.ports.transport import AuthSessionTransport
from app.infrastructure.auth.session.timer_utc import UtcAuthSessionTimer
from app.infrastructure.exceptions.gateway import DataMapperError

log = logging.getLogger(__name__)


class AuthSessionService:
    def __init__(
        self,
        auth_session_gateway: AuthSessionGateway,
        auth_session_transport: AuthSessionTransport,
        auth_transaction_manager: AuthSessionTransactionManager,
        auth_session_id_generator: StrAuthSessionIdGenerator,
        auth_session_timer: UtcAuthSessionTimer,
    ):
        self._auth_session_gateway = auth_session_gateway
        self._auth_session_transport = auth_session_transport
        self._auth_transaction_manager = auth_transaction_manager
        self._auth_session_id_generator = auth_session_id_generator
        self._auth_session_timer = auth_session_timer
        self._cached_auth_session: AuthSession | None = None

    async def create_session(self, user_id: UserId) -> None:
        """
        :raises AuthenticationError:
        """
        log.debug("Create auth session: started. User ID: '%s'.", user_id.value)

        auth_session_id: str = self._auth_session_id_generator()
        expiration: datetime = self._auth_session_timer.auth_session_expiration
        auth_session = AuthSession(
            id_=auth_session_id,
            user_id=user_id,
            expiration=expiration,
        )

        try:
            self._auth_session_gateway.add(auth_session)
            await self._auth_transaction_manager.commit()

        except DataMapperError as error:
            raise AuthenticationError(AUTH_IS_UNAVAILABLE) from error

        self._auth_session_transport.deliver(auth_session)

        log.debug(
            "Create auth session: done. User ID: '%s', Auth session id: '%s'.",
            user_id.value,
            auth_session.id_,
        )

    async def get_authenticated_user_id(self) -> UserId:
        """
        :raises AuthenticationError:
        """
        log.debug("Get authenticated user ID: started.")

        raw_auth_session = await self._load_current_session()
        valid_auth_session = await self._validate_and_extend_session(raw_auth_session)

        log.debug(
            "Get authenticated user ID: done. Auth session ID: %s. User ID: %s.",
            valid_auth_session.id_,
            valid_auth_session.user_id.value,
        )
        return valid_auth_session.user_id

    async def invalidate_current_session(self) -> None:
        log.debug("Invalidate current session: started. Auth session ID: unknown.")

        auth_session_id: str | None = self._auth_session_transport.extract_id()
        if auth_session_id is None:
            log.warning(
                "Invalidate current session failed: partially failed. "
                "Session ID can't be extracted from transport. "
                "Auth session can't be identified.",
            )
            return

        log.debug(
            "Invalidate current session: in progress. Auth session id: %s.",
            auth_session_id,
        )

        self._auth_session_transport.remove_current()

        auth_session: AuthSession | None = None
        try:
            auth_session = await self._auth_session_gateway.read_by_id(auth_session_id)

        except DataMapperError as error:
            log.error("%s: '%s'", AUTH_SESSION_EXTRACTION_FAILED, error)

        if auth_session is None:
            log.warning(
                "Invalidate current session failed: partially failed. "
                "Session ID was removed from transport, "
                "but auth session was not found in storage.",
            )
            return

        try:
            await self._auth_session_gateway.delete(auth_session.id_)
            await self._auth_transaction_manager.commit()

        except DataMapperError:
            log.warning(
                (
                    "Invalidate current session failed: partially failed. "
                    "Session ID was removed from transport, "
                    "but auth session was not deleted from storage. "
                    "Auth session ID: '%s'."
                ),
                auth_session.id_,
            )

    async def invalidate_all_sessions_for_user(self, user_id: UserId) -> None:
        """
        :raises DataMapperError:
        """
        log.debug(
            "Invalidate all sessions for user: started. User id: '%s'.",
            user_id.value,
        )

        await self._auth_session_gateway.delete_all_for_user(user_id)
        await self._auth_transaction_manager.commit()

        log.debug(
            "Invalidate all sessions for user: done. User id: '%s'.",
            user_id.value,
        )

    async def _load_current_session(self) -> AuthSession:
        """
        :raises AuthenticationError:
        """
        log.debug("Load current auth session: started. Auth session id: unknown.")
        if self._cached_auth_session is not None:
            cached_auth_session = self._cached_auth_session
            log.debug(
                "Load current auth session: done (from cache). Auth session id: %s.",
                cached_auth_session.id_,
            )
            return cached_auth_session

        auth_session_id: str | None = self._auth_session_transport.extract_id()
        if auth_session_id is None:
            log.debug(AUTH_SESSION_NOT_FOUND)
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        log.debug(
            "Load current auth session: in progress. Auth session id: %s.",
            auth_session_id,
        )

        try:
            auth_session: (
                AuthSession | None
            ) = await self._auth_session_gateway.read_by_id(
                auth_session_id,
            )
        except DataMapperError as error:
            log.error("%s: '%s'", AUTH_SESSION_EXTRACTION_FAILED, error)
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED) from error

        if auth_session is None:
            log.debug(AUTH_SESSION_NOT_FOUND)
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        self._cached_auth_session = auth_session

        log.debug(
            "Load current auth session: done. Auth session id: %s.",
            auth_session.id_,
        )
        return auth_session

    async def _validate_and_extend_session(
        self,
        auth_session: AuthSession,
    ) -> AuthSession:
        """
        :raises AuthenticationError:
        """
        log.debug(
            "Validate and extend auth session: started. Auth session id: %s.",
            auth_session.id_,
        )

        now = self._auth_session_timer.current_time
        if auth_session.expiration <= now:
            log.debug(AUTH_SESSION_EXPIRED)
            raise AuthenticationError(AUTH_NOT_AUTHENTICATED)

        if (
            auth_session.expiration - now
            > self._auth_session_timer.refresh_trigger_interval
        ):
            log.debug(
                "Validate and extend auth session: validated without extension. "
                "Auth session id: %s.",
                auth_session.id_,
            )
            return auth_session

        original_expiration = auth_session.expiration
        auth_session.expiration = self._auth_session_timer.auth_session_expiration

        try:
            await self._auth_session_gateway.update(auth_session)
            await self._auth_transaction_manager.commit()

        except DataMapperError as error:
            log.error("%s: '%s'", AUTH_SESSION_EXTENSION_FAILED, error)
            auth_session.expiration = original_expiration
            return auth_session

        self._auth_session_transport.deliver(auth_session)

        self._cached_auth_session = auth_session

        log.debug(
            "Validate and extend auth session: done. Auth session id: %s.",
            auth_session.id_,
        )
        return auth_session
