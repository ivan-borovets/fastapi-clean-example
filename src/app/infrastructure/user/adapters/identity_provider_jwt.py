from app.application.user.ports.identity_provider import IdentityProvider
from app.application.user.protocols.account_user_service import AccountUserService
from app.application.user.record_session import SessionRecord
from app.application.user.services.session import SessionService
from app.domain.user.entity_user import User
from app.domain.user.enums import UserRoleEnum
from app.domain.user.vo_user import UserId


class JwtIdentityProvider(IdentityProvider):
    def __init__(
        self,
        session_service: SessionService,
        account_user_service: AccountUserService,
    ):
        self._session_service = session_service
        self._account_user_service = account_user_service

    async def get_current_user_id(self) -> UserId:
        """
        :raises AdapterError:
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        :raises SessionExpired:
        """
        session: SessionRecord = await self._session_service.get_current_session()

        return session.user_id

    async def get_current_user_roles(self) -> set[UserRoleEnum]:
        """
        :raises AdapterError:
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        :raises SessionExpired:
        :raises UserNotFoundById:
        """
        user_id: UserId = await self.get_current_user_id()

        user: User = await self._account_user_service.get_user_by_id(user_id)

        return user.roles
