import logging

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.identity_provider import IdentityProvider
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.constants import (
    AUTHZ_NO_CURRENT_USER,
    AUTHZ_NOT_AUTHORIZED,
)
from app.domain.entities.user import User

log = logging.getLogger(__name__)


class CurrentUserService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_command_gateway: UserCommandGateway,
        access_revoker: AccessRevoker,
    ) -> None:
        self._identity_provider = identity_provider
        self._user_command_gateway = user_command_gateway
        self._access_revoker = access_revoker

    async def get_current_user(self, for_update: bool = False) -> User:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        current_user_id = await self._identity_provider.get_current_user_id()
        user: User | None = await self._user_command_gateway.read_by_id(
            current_user_id,
            for_update=for_update,
        )
        if user is None or not user.is_active:
            log.warning("%s ID: %s.", AUTHZ_NO_CURRENT_USER, current_user_id)
            await self._access_revoker.remove_all_user_access(current_user_id)
            raise AuthorizationError(AUTHZ_NOT_AUTHORIZED)

        return user
