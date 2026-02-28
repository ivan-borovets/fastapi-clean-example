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
from app.core.common.value_objects.raw_password import RawPassword

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SetUserPasswordRequest:
    user_id: UUID
    password: str


class SetUserPassword:
    """
    - Open to admins.
    - Admins can set passwords of subordinate users.
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

    async def execute(self, request: SetUserPasswordRequest) -> None:
        logger.info("Set user password: started.")

        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=UserRole.USER,
            ),
        )
        user_id = UserId(request.user_id)
        password = RawPassword(request.password)
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

        await self._user_service.change_password(
            user,
            password,
            now=self._utc_timer.now,
        )
        await self._transaction_manager.commit()

        logger.info("Set user password: done.")
