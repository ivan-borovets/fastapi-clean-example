import logging
from dataclasses import dataclass
from uuid import UUID

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization.authorize import (
    authorize,
)
from app.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import (
    UserNotFoundByIdError,
)
from app.domain.services.user import UserService
from app.domain.value_objects.user_id import UserId

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GrantAdminRequest:
    user_id: UUID


class GrantAdminInteractor:
    """
    - Open to super admins.
    - Grants admin rights to a specified user.
    - Super admin rights cannot be changed.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: GrantAdminRequest) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises UserNotFoundByIdError:
        :raises RoleChangeNotPermittedError:
        """
        log.info("Grant admin: started. Target user ID: '%s'.", request_data.user_id)

        current_user = await self._current_user_service.get_current_user()

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.ADMIN,
            ),
        )

        user_id = UserId(request_data.user_id)
        user: User | None = await self._user_command_gateway.read_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByIdError(user_id)

        if self._user_service.toggle_user_admin_role(user, is_admin=True):
            await self._transaction_manager.commit()

        log.info("Grant admin: done. Target user ID: '%s'.", user.id_.value)
