import logging
from uuid import UUID

from app.base.b_application.interactors import InteractorStrict
from app.common.b_application.enums import ResponseStatusEnum
from app.common.b_application.exceptions import GatewayError
from app.common.b_application.persistence.committer import Committer
from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.enums import UserRoleEnum
from app.distinct.user.a_domain.exceptions.existence import UsernameAlreadyExists
from app.distinct.user.a_domain.vo_user import Username
from app.distinct.user.b_application.exceptions import (
    AuthenticationError,
    AuthorizationError,
)
from app.distinct.user.b_application.gateways.user import UserGateway
from app.distinct.user.b_application.ports.password_hasher import PasswordHasher
from app.distinct.user.b_application.ports.user_id_generator import UserIdGenerator
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.create_user.b_payload import (
    CreateUserRequest,
    CreateUserResponse,
)

log = logging.getLogger(__name__)


class CreateUserInteractor(InteractorStrict[CreateUserRequest, CreateUserResponse]):
    def __init__(
        self,
        auth_service: AuthService,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
        user_gateway: UserGateway,
        committer: Committer,
    ):
        self._auth_service = auth_service
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher
        self._user_gateway = user_gateway
        self._committer = committer

    async def __call__(self, request_data: CreateUserRequest) -> CreateUserResponse:
        """
        :raises AuthenticationError:
        :raises AuthorizationError:
        :raises UsernameAlreadyExists:
        :raises GatewayError:
        """
        log.info("Create user: '%s'.", request_data.username)
        try:
            await self._auth_service.check_authorization(UserRoleEnum.ADMIN)
        except (AuthenticationError, AuthorizationError):
            raise

        log.debug("Checking username '%s' uniqueness.", request_data.username)
        try:
            if not await self._user_gateway.is_username_unique(
                Username(request_data.username)
            ):
                raise UsernameAlreadyExists(request_data.username)
        except GatewayError:
            raise

        log.debug("Generating user id.")
        user_id: UUID = self._user_id_generator()

        log.debug("Generating password hash for user with id '%s'", user_id)
        password_hash: bytes = self._password_hasher.hash(request_data.password)

        log.debug(
            "Creating user, id '%s', username '%s'.",
            user_id,
            request_data.username,
        )
        user: User = User.create(
            user_id=user_id,
            username=request_data.username,
            password_hash=password_hash,
        )

        log.debug("Setting given roles.")
        request_data.roles.add(UserRoleEnum.USER)
        user.roles = request_data.roles

        log.debug(
            "Trying to save user with id '%s', username '%s'.",
            user_id,
            request_data.username,
        )
        try:
            await self._user_gateway.create(user)
            await self._committer.commit()
        except GatewayError:
            raise

        log.info(
            "New user, id: '%s', username '%s', roles '%s' saved.",
            user_id,
            request_data.username,
            ", ".join(str(role.value) for role in user.roles),
        )
        return CreateUserResponse(request_data.username, ResponseStatusEnum.CREATED)
