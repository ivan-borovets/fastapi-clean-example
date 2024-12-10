import logging

from app.application.user.exceptions import AuthorizationError
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.value_objects import UserId

log = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway

    async def check_authorization(self, role_required: UserRoleEnum) -> None:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        :raises DataMapperError:
        """
        log.debug("Check authorization: started.")

        current_user_roles: set[UserRoleEnum] = await self.get_current_user_roles()

        if role_required not in current_user_roles:
            log.debug("Check authorization: done. User isn't authorized.")
            raise AuthorizationError("Not authorized.")

        log.debug("Check authorization: done. User is authorized.")

    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        :raises DataMapperError:
        """
        log.debug("Get current user roles: started.")

        current_user_id: UserId = await self._identity_provider.get_current_user_id()

        user: User | None = await self._user_data_gateway.read_by_id(current_user_id)
        if user is None:
            log.error("Get current user roles: failed. No user found.")
            raise AuthorizationError("Not authorized.")

        log.debug("Get current user id: done.")
        return user.roles
