import logging
from uuid import UUID

from app.application.committer import Committer
from app.application.user.data_gateways.user import UserDataGateway
from app.application.user.ports.password_hasher import PasswordHasher
from app.application.user.ports.user_id_generator import UserIdGenerator
from app.application.user.protocols.account_user_service import AccountUserService
from app.application.user.protocols.admin_user_service import AdminUserService
from app.domain.user.entity_user import User
from app.domain.user.exceptions.existence import UsernameAlreadyExists
from app.domain.user.exceptions.non_existence import (
    UserNotFoundById,
    UserNotFoundByUsername,
)
from app.domain.user.vo_user import UserId, Username

log = logging.getLogger(__name__)


class UserService(AccountUserService, AdminUserService):
    def __init__(
        self,
        user_data_gateway: UserDataGateway,
        user_id_generator: UserIdGenerator,
        password_hasher: PasswordHasher,
        committer: Committer,
    ):
        self._user_data_gateway = user_data_gateway
        self._user_id_generator = user_id_generator
        self._password_hasher = password_hasher
        self._committer = committer

    async def check_username_uniqueness(self, username: Username) -> None:
        """
        :raises DataGatewayError:
        :raises UsernameAlreadyExists:
        """
        log.debug("Check username uniqueness: started. Username: '%s'.", username.value)

        if not await self._user_data_gateway.is_username_unique(username):
            raise UsernameAlreadyExists(username.value)

        log.debug("Check username uniqueness: done. Username: '%s'.", username.value)

    async def create_user(self, username: Username, password: str) -> User:
        log.debug("Create user: started. Username: '%s'.", username.value)

        user_id: UUID = self._user_id_generator()
        password_hash: bytes = self._password_hasher.hash(password)
        user: User = User.create(
            user_id=user_id,
            username=username.value,
            password_hash=password_hash,
        )

        log.debug("Create user: done. Username: '%s'.", username.value)

        return user

    async def save_user(self, user: User) -> None:
        """
        :raises DataGatewayError:
        """
        log.debug("Save user: started. Username: '%s'.", user.username.value)

        await self._user_data_gateway.save(user)

        await self._committer.commit()

        log.debug(
            "Save user: done. User: '%s', '%s', '%s'.",
            user.id_.value,
            user.username.value,
            ", ".join(str(role.value) for role in user.roles),
        )

    async def get_user_by_username(
        self, username: Username, for_update: bool = False
    ) -> User:
        """
        :raises DataGatewayError:
        :raises UserNotFoundByUsername:
        """
        log.debug("Get user by username: started. Username: '%s'.", username.value)

        user: User | None = await self._user_data_gateway.read_by_username(
            username, for_update=for_update
        )

        if user is None:
            raise UserNotFoundByUsername(username.value)

        log.debug("Get user by username: done. Username: '%s'.", username.value)
        return user

    async def get_user_by_id(self, user_id: UserId) -> User:
        """
        :raises DataGatewayError:
        :raises UserNotFoundById:
        """
        log.debug("Get user by id: started. User id: '%s'.", user_id.value)

        user: User | None = await self._user_data_gateway.read_by_id(user_id)
        if user is None:
            raise UserNotFoundById(user_id)

        log.debug("Get user by id: done. Username: '%s'.", user_id.value)
        return user
