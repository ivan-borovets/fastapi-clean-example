import logging

from app.application.base.interactors import InteractorStrict
from app.application.committer import Committer
from app.application.enums import ResponseStatusEnum
from app.domain.user.entity import User
from app.domain.user.exceptions.existence import UsernameAlreadyExists
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username
from app.infrastructure.session.adapters_application.identity_provider_session import (
    SessionIdentityProvider,
)
from app.infrastructure.session.exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)
from app.infrastructure.session.scenarios.sign_up.payload import (
    SignUpRequest,
    SignUpResponse,
)
from app.infrastructure.user.adapters_application.user_data_mapper_sqla import (
    SqlaUserDataMapper,
)

log = logging.getLogger(__name__)


class SignUpInteractor(InteractorStrict[SignUpRequest, SignUpResponse]):
    """
    :raises AlreadyAuthenticatedError:
    :raises DomainFieldError:
    :raises DataMapperError:
    :raises UsernameAlreadyExists:
    """

    def __init__(
        self,
        session_identity_provider: SessionIdentityProvider,
        sqla_user_data_mapper: SqlaUserDataMapper,
        user_service: UserService,
        committer: Committer,
    ):
        self._session_identity_provider = session_identity_provider
        self._sqla_user_data_mapper = sqla_user_data_mapper
        self._user_service = user_service
        self._committer = committer

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        log.info("Sign up: started. Username: '%s'.", request_data.username)

        try:
            await self._session_identity_provider.get_current_user_id()
            raise AlreadyAuthenticatedError(
                "You are already authenticated. Consider logging out."
            )
        except AuthenticationError:
            pass

        username: Username = Username(request_data.username)
        password: RawPassword = RawPassword(request_data.password)

        if not await self._sqla_user_data_mapper.is_username_unique(username):
            raise UsernameAlreadyExists(username.value)

        user: User = self._user_service.create_user(username, password)

        await self._sqla_user_data_mapper.save(user)
        await self._committer.commit()

        log.info("Sign up: done. Username: '%s'.", user.username.value)
        return SignUpResponse(user.username.value, ResponseStatusEnum.CREATED)
