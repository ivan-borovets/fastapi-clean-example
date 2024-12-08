import logging

from app.application.user_helpers.exceptions import AuthorizationError
from app.application.user_helpers.ports.identity_provider import IdentityProvider
from app.domain.user.enums import UserRoleEnum

log = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
    ):
        self._identity_provider = identity_provider

    async def check_authorization(self, role_required: UserRoleEnum) -> None:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        """
        log.debug("Check authorization: started.")

        current_user_roles: set[UserRoleEnum] = (
            await self._identity_provider.get_current_user_roles()
        )

        if role_required not in current_user_roles:
            raise AuthorizationError("Authorization failed.")
