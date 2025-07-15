import logging
from dataclasses import dataclass

from app.application.common.permissions import AnyOf, IsSelf, IsSuperior
from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.ports.user_command_gateway import UserCommandGateway
from app.application.common.services.authorization import AuthorizationService
from app.application.common.services.current_user import CurrentUserService
from app.domain.entities.user import User
from app.domain.exceptions.user import UserNotFoundByUsernameError
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password.raw_password import RawPassword
from app.domain.value_objects.username.username import Username

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordRequest:
    username: str
    password: str


class ChangePasswordInteractor:
    """
    Open to authenticated users.
    Changes the user's password.
    The current user can change their own password.
    Admins can change passwords of subordinate users.

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
            username,
            for_update=True,
        )
        if user is None:
            raise UserNotFoundByUsernameError(username)

        # Declarative authorization: can change own or subordinate's password
        self._authorization_service.authorize(
            current_user,
            AnyOf(IsSelf(), IsSuperior()),
            target_user=user,
        )

        self._user_service.change_password(user, password)
        await self._transaction_manager.commit()

        log.info("Change password: done.")
