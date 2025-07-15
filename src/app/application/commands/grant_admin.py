import logging
from dataclasses import dataclass

from app.application.common.permissions import CanManageRole
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.domain.services.user import UserService
from app.domain.value_objects.username.username import Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GrantAdminRequest:
    username: str


class GrantAdminInteractor:
    """
    Open to super admins.
    Grants admin rights to a specified user.
    Super admin rights can not be changed.

    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises UserNotFoundByUsername:
    :raises RoleChangeNotPermitted:
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        authorization_service: AuthorizationService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._authorization_service = authorization_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def __call__(self, request_data: GrantAdminRequest) -> None:
        log.info(
            "Grant admin: started. Username: '%s'.",
            request_data.username,
        )

        current_user = await self._current_user_service.get_current_user()

        # Declarative authorization: only users who can manage ADMIN role
        self._authorization_service.authorize(
            current_user,
            CanManageRole(UserRole.ADMIN),
        )

        username = Username(request_data.username)
        user: User | None = await self._user_command_gateway.read_by_username(
            username,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByUsernameError(username)

        self._user_service.toggle_user_admin_role(user, is_admin=True)
        await self._transaction_manager.commit()

        log.info("Grant admin: done. Username: '%s'.", user.username.value)
