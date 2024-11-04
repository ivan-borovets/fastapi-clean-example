import logging

from app.application.base.interactors import InteractorStrict
from app.application.enums import ResponseStatusEnum
from app.application.user.protocols.admin_user_service import AdminUserService
from app.application.user.services.authorization import AuthorizationService
from app.application.user.services.session import SessionService
from app.domain.user.entity_user import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.vo_user import Username
from app.scenarios.user.inactivate_user.application_payload import (
    InactivateUserRequest,
    InactivateUserResponse,
)

log = logging.getLogger(__name__)


class InactivateUserInteractor(
    InteractorStrict[InactivateUserRequest, InactivateUserResponse]
):
    """
    :raises AuthenticationError:
    :raises AuthorizationError:
    :raises DataGatewayError:
    :raises UserNotFoundByUsername:
    """

    def __init__(
        self,
        authorization_service: AuthorizationService,
        admin_user_service: AdminUserService,
        session_service: SessionService,
    ):
        self._authorization_service = authorization_service
        self._admin_user_service = admin_user_service
        self._session_service = session_service

    async def __call__(
        self, request_data: InactivateUserRequest
    ) -> InactivateUserResponse:
        log.info(
            "Inactivate admin by admin: started. Username: '%s'.", request_data.username
        )
        await self._authorization_service.authorize_and_try_prolong(UserRoleEnum.ADMIN)

        username_vo: Username = Username(request_data.username)

        user: User = await self._admin_user_service.get_user_by_username(
            username=username_vo, for_update=True
        )
        user.inactivate()

        await self._admin_user_service.save_user(user)

        await self._session_service.delete_all_sessions_by_user_id(user.id_)
        log.info(
            "Inactivate admin by admin: finished. Username: '%s'.", user.username.value
        )
        return InactivateUserResponse(user.username.value, ResponseStatusEnum.UPDATED)
