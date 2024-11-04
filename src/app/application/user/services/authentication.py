import logging

from app.application.exceptions import AdapterError, DataGatewayError
from app.application.user.exceptions import AuthenticationError, SessionExpired
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.ports.password_hasher import PasswordHasher
from app.domain.user.entity_user import User
from app.domain.user.exceptions.non_existence import SessionNotFoundById

log = logging.getLogger(__name__)


class AuthenticationService:
    def __init__(
        self,
        password_hasher: PasswordHasher,
        identity_provider: IdentityProvider,
    ):
        self._password_hasher = password_hasher
        self._identity_provider = identity_provider

    def authenticate(self, user: User, password: str) -> None:
        """
        :raises AuthenticationError:
        """
        log.debug("Authenticate: started. Username: '%s'.", user.username.value)

        if not user.is_active:
            raise AuthenticationError(
                "Your account is inactive. Please contact support."
            )

        if not self._password_hasher.verify(
            raw_password=password,
            hashed_password=user.password_hash.value,
        ):
            raise AuthenticationError("Wrong password.")

        log.debug("Authenticate: done. Username: '%s'.", user.username.value)

    async def is_authenticated(self) -> bool:
        log.debug("Is authenticated: started.")

        try:
            await self._identity_provider.get_current_user_id()
        except (
            AdapterError,
            SessionNotFoundById,
            DataGatewayError,
            SessionExpired,
        ) as error:
            log.error("Authentication failed: '%s'", error)
            return False

        log.debug("Is authenticated: done.")
        return True
