import logging
from typing import Final

from app.core.common.authorization.exceptions import AuthorizationError
from app.core.common.authorization.ports import AuthzUserFinder
from app.core.common.entities.user import User
from app.core.common.ports.access_revoker import AccessRevoker
from app.core.common.ports.identity_provider import IdentityProvider

AUTHZ_NO_CURRENT_USER: Final[str] = "Failed to retrieve current user. Removing all access."

logger = logging.getLogger(__name__)


class CurrentUserService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        authz_user_finder: AuthzUserFinder,
        access_revoker: AccessRevoker,
    ) -> None:
        self._identity_provider = identity_provider
        self._authz_user_finder = authz_user_finder
        self._access_revoker = access_revoker

    async def get_current_user(self, *, for_update: bool = False) -> User:
        current_user_id = await self._identity_provider.get_current_user_id()
        user = await self._authz_user_finder.get_by_id(current_user_id, for_update=for_update)
        if user is None or not user.is_active:
            logger.warning("%s ID: %s.", AUTHZ_NO_CURRENT_USER, current_user_id)
            await self._access_revoker.remove_all_user_access(current_user_id)
            raise AuthorizationError
        return user
