import logging

from app.application.exceptions import DataGatewayError
from app.application.user_helpers.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.application.user_helpers.ports.identity_provider import IdentityProvider
from app.domain.user.entity import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.exceptions.non_existence import UserNotFoundById
from app.domain.user.value_objects import UserId
from app.infrastructure.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)

log = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
    ):
        self._identity_provider = identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper

    async def check_authorization(self, role_required: UserRoleEnum) -> None:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        """
        log.debug("Check authorization: started.")

        current_user_roles: set[UserRoleEnum] = await self.get_current_user_roles()

        if role_required not in current_user_roles:
            raise AuthorizationError("Authorization failed.")

    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AuthenticationError:
        """
        log.debug("Get current user roles: started.")

        current_user_id: UserId = await self._identity_provider.get_current_user_id()

        try:
            user: User | None = await self._sqla_user_data_mapper.read_by_id(
                current_user_id
            )
            if user is None:
                raise UserNotFoundById(current_user_id)
        except (DataGatewayError, UserNotFoundById) as error:
            raise AuthenticationError("Not authenticated") from error

        log.debug("Get current user id: done.")
        return user.roles
