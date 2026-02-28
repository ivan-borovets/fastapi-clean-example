from app.core.common.entities.types_ import UserId
from app.core.common.ports.access_revoker import AccessRevoker
from app.infrastructure.auth_ctx.service import AuthService


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    async def remove_all_user_access(self, user_id: UserId) -> None:
        await self._auth_service.revoke_all_sessions(user_id)
