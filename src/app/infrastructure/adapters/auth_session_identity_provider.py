from app.core.common.entities.types_ import UserId
from app.core.common.ports.identity_provider import IdentityProvider
from app.infrastructure.auth_ctx.service import AuthService


class AuthSessionIdentityProvider(IdentityProvider):
    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    async def get_current_user_id(self) -> UserId:
        return await self._auth_service.get_current_user_id()
