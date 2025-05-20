import logging
from dataclasses import dataclass

from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user.entity import User
from app.domain.entities.user.value_objects import RawPassword, Username
from app.domain.exceptions.user import UserNotFoundByUsername
from app.domain.services.user import UserService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordRequest:
    username: str
    password: str


class ChangePasswordInteractor:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises UserNotFoundByUsername:
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

    async def __call__(self, request_data: ChangePasswordRequest) -> None:
        log.info("Change password: started.")

        current_user = await self._current_user_service.get_current_user()

        username = Username(request_data.username)
        password = RawPassword(request_data.password)
        user: User | None = await self._user_command_gateway.read_by_username(
            username, for_update=True
        )
        if user is None:
            raise UserNotFoundByUsername(username)

        try:
            self._authorization_service.authorize_for_self(
                current_user, target_user=user
            )
        except AuthorizationError:
            self._authorization_service.authorize_for_subordinate_role(
                current_user, target_role=user.role
            )

        self._user_service.change_password(user, password)
        await self._transaction_manager.commit()

        log.info("Change password: finished.")
