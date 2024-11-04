import logging

from app.base.b_application.interactors import InteractorStrict
from app.common.b_application.exceptions import GatewayError
from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.b_application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.list_users.b_payload import (
    ListUsersRequest,
    ListUsersResponse,
    ListUsersResponseElement,
)

log = logging.getLogger(__name__)


class ListUsersInteractor(InteractorStrict[ListUsersRequest, ListUsersResponse]):
    def __init__(
        self,
        auth_service: AuthService,
        user_gateway: UserGateway,
    ):
        self._auth_service = auth_service
        self._user_gateway = user_gateway

    async def __call__(self, request_data: ListUsersRequest) -> ListUsersResponse:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        :raises GatewayError:
        """
        log.info("List users.")
        try:
            await self._auth_service.check_authorization(UserRoleEnum.ADMIN)
        except (AuthenticationError, AuthorizationError):
            raise

        log.debug("Retrieving list of users.")
        try:
            users: list[User] = await self._user_gateway.get_all(
                request_data.limit, request_data.offset
            )
        except GatewayError:
            raise

        response: ListUsersResponse = ListUsersResponse(
            [
                ListUsersResponseElement(
                    user.id_.value,
                    user.username.value,
                    user.roles,
                    user.is_active,
                )
                for user in users
            ]
        )

        log.info("List users: response is ready.")
        return response
