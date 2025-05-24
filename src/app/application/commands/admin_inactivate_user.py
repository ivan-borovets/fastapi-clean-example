import logging
from dataclasses import dataclass

from app.application.common.ports.access_revoker import AccessRevoker
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.transaction_manager import TransactionManager
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.domain.services.user import UserService
from app.domain.value_objects.username.username import Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class InactivateUserRequest:
    username: str


class InactivateUserInteractor:
    """
    :raises AuthenticationError:
    :raises DataMapperError:
    :raises AuthorizationError:
    :raises DomainFieldError:
    :raises UserNotFoundByUsername:
    :raises ActivationChangeNotPermitted:
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        authorization_service: AuthorizationService,
        user_command_gateway: UserCommandGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
        access_revoker: AccessRevoker,
    ):
        self._current_user_service = current_user_service
        self._authorization_service = authorization_service
        self._user_command_gateway = user_command_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager
        self._access_revoker = access_revoker

    async def __call__(self, request_data: InactivateUserRequest) -> None:
        log.info(
            "Inactivate user by admin: started. Username: '%s'.",
            request_data.username,
        )

        current_user = await self._current_user_service.get_current_user()
        self._authorization_service.authorize_for_subordinate_role(
            current_user,
            target_role=UserRole.USER,
        )

        username = Username(request_data.username)
        user: User | None = await self._user_command_gateway.read_by_username(
            username,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByUsernameError(username)

        self._authorization_service.authorize_for_subordinate_role(
            current_user,
            target_role=user.role,
        )

        self._user_service.toggle_user_activation(user, is_active=False)
        await self._transaction_manager.commit()
        await self._access_revoker.remove_all_user_access(user.id_)

        log.info(
            "Inactivate user by admin: finished. Username: '%s'.",
            user.username.value,
        )
