import logging

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.identity_provider import IdentityProvider
from app.domain.entities.user.entity import User

log = logging.getLogger(__name__)


class CurrentUserService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_command_gateway: UserCommandGateway,
    ):
        self._identity_provider = identity_provider
        self._user_command_gateway = user_command_gateway

    async def get_current_user(self) -> User:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        current_user_id = await self._identity_provider.get_current_user_id()
        user: User | None = await self._user_command_gateway.read_by_id(current_user_id)
        if user is None:
            log.debug("Failed to retrieve current user.")
            raise AuthorizationError("Not authorized.")
        return user
