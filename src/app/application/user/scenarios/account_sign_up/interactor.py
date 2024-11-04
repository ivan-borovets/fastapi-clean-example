import logging

from app.application.base.interactors import InteractorStrict
from app.application.committer import Committer
from app.application.enums import ResponseStatusEnum
from app.application.user.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.ports.user_data_gateway import UserDataGateway
from app.application.user.scenarios.account_sign_up.payload import (
    SignUpRequest,
    SignUpResponse,
)
from app.domain.user.entity import User
from app.domain.user.exceptions.existence import UsernameAlreadyExists
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username

log = logging.getLogger(__name__)


class SignUpInteractor(InteractorStrict[SignUpRequest, SignUpResponse]):
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataGatewayError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        user_service: UserService,
        committer: Committer,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._committer = committer

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._identity_provider.get_current_user_id()
            raise AlreadyAuthenticatedError(
                "You are already authenticated. Consider logging out."
            )
        except AuthenticationError:
            pass

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        if not await self._user_data_gateway.is_username_unique(username):
            raise UsernameAlreadyExists(username.value)

        user: User = self._user_service.create_user(username, password)

        await self._user_data_gateway.save(user)
        await self._committer.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(user.username.value, ResponseStatusEnum.CREATED)
