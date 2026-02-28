import logging
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import TypedDict
from uuid import UUID

from app.core.commands.exceptions import UsernameAlreadyExistsError
from app.core.commands.ports.flusher import Flusher
from app.core.commands.ports.transaction_manager import TransactionManager
from app.core.commands.ports.user_tx_storage import UserTxStorage
from app.core.commands.ports.utc_timer import UtcTimer
from app.core.common.authorization.authorize import authorize
from app.core.common.authorization.current_user_service import CurrentUserService
from app.core.common.authorization.permissions import CanManageRole, RoleManagementContext
from app.core.common.entities.types_ import UserRole
from app.core.common.factories.id_factory import create_user_id
from app.core.common.services.user import UserService
from app.core.common.value_objects.raw_password import RawPassword
from app.core.common.value_objects.username import Username

logger = logging.getLogger(__name__)


class UserRoleRequestEnum(StrEnum):
    USER = "user"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    username: str
    password: str
    role: UserRoleRequestEnum


class CreateUserResponse(TypedDict):
    id: UUID
    created_at: datetime


class CreateUser:
    """
    - Open to admins.
    - Creates new user, including admins, if the username is unique.
    - Only super admins can create new admins.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        utc_timer: UtcTimer,
        user_tx_storage: UserTxStorage,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._utc_timer = utc_timer
        self._user_tx_storage = user_tx_storage
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        logger.info("Create user: started.")

        current_user = await self._current_user_service.get_current_user()
        role = UserRole(request.role)
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=role,
            ),
        )
        username = Username(request.username)
        password = RawPassword(request.password)
        user = await self._user_service.create_user_with_raw_password(
            user_id=create_user_id(),
            username=username,
            raw_password=password,
            now=self._utc_timer.now,
            role=role,
        )
        self._user_tx_storage.add(user)
        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        logger.info("Create user: done.")
        return CreateUserResponse(
            id=user.id_,
            created_at=user.created_at.value,
        )
