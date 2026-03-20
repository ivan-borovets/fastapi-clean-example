import logging
from dataclasses import dataclass
from uuid import UUID

from app.core.commands.exceptions import UserNotFoundError
from app.core.commands.ports.transaction_manager import TransactionManager
from app.core.commands.ports.user_tx_storage import UserTxStorage
from app.core.commands.ports.utc_timer import UtcTimer
from app.core.common.authorization.authorize import authorize
from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.authorization.permissions import (
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from app.core.common.entities.types_ import UserId, UserRole
from app.core.common.services.user import UserService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RevokeAdminRequest:
    user_id: UUID


class RevokeAdmin:
    """
    - Open to super admins.
    - Revokes admin rights from specified user.
    - Super admin rights cannot be changed
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_tx_storage: UserTxStorage,
        user_service: UserService,
        utc_timer: UtcTimer,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_tx_storage = user_tx_storage
        self._user_service = user_service
        self._utc_timer = utc_timer
        self._transaction_manager = transaction_manager

    async def execute(self, request: RevokeAdminRequest) -> None:
        logger.info("Revoke admin: started.")

        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.ADMIN,
            ),
        )
        user_id = UserId(request.user_id)
        user = await self._user_tx_storage.get_by_id(
            user_id,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundError

        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(
                subject=current_user,
                target=user,
            ),
        )
        if self._user_service.set_role(
            user,
            now=self._utc_timer.now,
            is_admin=False,
        ):
            await self._transaction_manager.commit()

        logger.info("Revoke admin: done.")
