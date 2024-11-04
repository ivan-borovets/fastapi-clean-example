import logging

from app.base.b_application.interactors import InteractorStrict
from app.common.b_application.enums import ResponseStatusEnum
from app.common.b_application.exceptions import GatewayError
from app.common.b_application.persistence.committer import Committer
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.exceptions.non_existence import UserNotFoundByUsername
from app.distinct.user.a_domain.vo_user import Username
from app.distinct.user.b_application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.reactivate_user.b_payload import (
    ReactivateUserRequest,
    ReactivateUserResponse,
)

log = logging.getLogger(__name__)


class ReactivateUserInteractor(
    InteractorStrict[ReactivateUserRequest, ReactivateUserResponse]
):
    def __init__(
        self,
        auth_service: AuthService,
        user_gateway: UserGateway,
        committer: Committer,
    ):
        self._auth_service = auth_service
        self._user_gateway = user_gateway
        self._committer = committer

    async def __call__(
        self, request_data: ReactivateUserRequest
    ) -> ReactivateUserResponse:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        log.info("Inactivate user: '%s'.", request_data.username)
        try:
            await self._auth_service.check_authorization(UserRoleEnum.ADMIN)
        except (AuthenticationError, AuthorizationError):
            raise

        try:
            await self._user_gateway.set_activation_status_by_username(
                Username(request_data.username), True
            )
            await self._committer.commit()

        except (UserNotFoundByUsername, GatewayError):
            raise

        log.info(
            "User '%s' inactivated.",
            request_data.username,
        )
        return ReactivateUserResponse(request_data.username, ResponseStatusEnum.UPDATED)
