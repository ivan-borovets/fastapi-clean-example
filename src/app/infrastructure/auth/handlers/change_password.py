import logging
from dataclasses import dataclass

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.application.common.services.current_user import CurrentUserService
from app.domain.services.user import UserService
from app.domain.value_objects.raw_password import RawPassword
from app.infrastructure.auth.exceptions import (
    AuthenticationChangeError,
    ReAuthenticationError,
)
from app.infrastructure.auth.session.constants import AUTH_INVALID_PASSWORD

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangePasswordRequest:
    current_password: str
    new_password: str


class ChangePasswordHandler:
    """
    - Open to authenticated users.
    - The current user can change their password.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_service: UserService,
        transaction_manager: TransactionManager,
    ):
        self._current_user_service = current_user_service
        self._user_service = user_service
        self._transaction_manager = transaction_manager

    async def execute(self, request_data: ChangePasswordRequest) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        :raises DomainFieldError:
        :raises AuthenticationChangeError:
        :raises ReAuthenticationError:
        """
        log.info("Change password: started.")

        current_user = await self._current_user_service.get_current_user(
            for_update=True
        )
        # TODO: update docs

        current_password = RawPassword(request_data.current_password)
        new_password = RawPassword(request_data.new_password)
        if current_password == new_password:
            raise AuthenticationChangeError("New password must differ from current.")

        if not self._user_service.is_password_valid(current_user, current_password):
            raise ReAuthenticationError(AUTH_INVALID_PASSWORD)

        self._user_service.change_password(current_user, new_password)
        await self._transaction_manager.commit()

        log.info("Change password: done. User ID: '%s'.", current_user.id_.value)
