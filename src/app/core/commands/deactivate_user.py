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
from app.core.common.ports.access_revoker import AccessRevoker
from app.core.common.services.user import UserService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DeactivateUserRequest:
    user_id: UUID


class DeactivateUser:
    """
    - Open to admins.
    - Soft-deletes existing user, making that user inactive.
    - Also deletes user's sessions.
    - Only super admins can deactivate other admins.
    - Super admins cannot be soft-deleted.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_tx_storage: UserTxStorage,
        user_service: UserService,
        utc_timer: UtcTimer,
        transaction_manager: TransactionManager,
        access_revoker: AccessRevoker,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_tx_storage = user_tx_storage
        self._user_service = user_service
        self._utc_timer = utc_timer
        self._transaction_manager = transaction_manager
        self._access_revoker = access_revoker

    async def execute(self, request: DeactivateUserRequest) -> None:
        logger.info("Deactivate user: started.")

        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
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
        if self._user_service.set_activation(
            user,
            now=self._utc_timer.now,
            is_active=False,
        ):
            await self._transaction_manager.commit()

        await self._access_revoker.remove_all_user_access(user.id_)

        logger.info("Deactivate user: done.")
