# pylint: disable=C0301 (line-too-long)
import logging
from dataclasses import dataclass

from app.application.common.ports.committer import Committer
from app.application.common.response_status_enum import ResponseStatusEnum
from app.domain.user.entity import User
from app.domain.user.exceptions.existence import UsernameAlreadyExists
from app.domain.user.service import UserService
from app.domain.user.value_objects import RawPassword, Username
from app.infrastructure.adapters.application.sqla_user_data_mapper import (
    SqlaUserDataMapper,
)
from app.infrastructure.session_context.common.application_adapters.session_identity_provider import (
    SessionIdentityProvider,
)
from app.infrastructure.session_context.common.authentication_exceptions import (
    AlreadyAuthenticatedError,
    AuthenticationError,
)

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class SignUpRequest:
    username: str
    password: str


@dataclass(frozen=True, slots=True)
class SignUpResponse:
    username: str
    status: ResponseStatusEnum


class SignUpInteractor:
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
