from app.core.common.entities.types_ import UserId
from app.infrastructure.auth_ctx.cookie_manager import CookieManager
from app.infrastructure.auth_ctx.exceptions import AuthenticationError
from app.infrastructure.auth_ctx.id_factory import create_session_id
from app.infrastructure.auth_ctx.jwt_processor import JwtProcessor
from app.infrastructure.auth_ctx.model import AuthSession, SessionId
from app.infrastructure.auth_ctx.sqla_transaction_manager import AuthSqlaTransactionManager
from app.infrastructure.auth_ctx.sqla_tx_storage import AuthSessionSqlaTxStorage
from app.infrastructure.auth_ctx.utc_timer import AuthSessionUtcTimer


class AuthService:
    def __init__(
        self,
        session_timer: AuthSessionUtcTimer,
        session_tx_storage: AuthSessionSqlaTxStorage,
        transaction_manager: AuthSqlaTransactionManager,
        jwt_processor: JwtProcessor,
        cookie_manager: CookieManager,
    ) -> None:
        self._session_timer = session_timer
        self._session_tx_storage = session_tx_storage
        self._transaction_manager = transaction_manager
        self._jwt_processor = jwt_processor
        self._cookie_manager = cookie_manager

    async def issue_session(self, user_id: UserId) -> None:
        session = AuthSession(
            id_=create_session_id(),
            user_id=user_id,
            expiration=self._session_timer.expiration_from_now,
        )
        self._session_tx_storage.add(session)
        await self._transaction_manager.commit()
        token = self._jwt_processor.encode(session)
        self._cookie_manager.stage_set(token)

    async def get_current_user_id(self) -> UserId:
        session_id = self._get_session_id()
        if session_id is None:
            raise AuthenticationError

        session = await self._session_tx_storage.get_by_id(session_id)
        if session is None:
            raise AuthenticationError

        if self._session_timer.is_expired(session):
            raise AuthenticationError

        if self._session_timer.needs_refresh(session):
            session.expiration = self._session_timer.expiration_from_now
            await self._session_tx_storage.update(session)
            await self._transaction_manager.commit()
            token = self._jwt_processor.encode(session)
            self._cookie_manager.stage_set(token)

        return session.user_id

    async def logout_current_session(self) -> None:
        self._cookie_manager.stage_delete()
        session_id = self._get_session_id()
        if session_id is not None:
            await self._session_tx_storage.delete(session_id)
            await self._transaction_manager.commit()

    async def revoke_all_sessions(self, user_id: UserId) -> None:
        await self._session_tx_storage.delete_all_for_user(user_id)
        await self._transaction_manager.commit()

    def _get_session_id(self) -> SessionId | None:
        token = self._cookie_manager.read()
        if token is None:
            return None
        return self._jwt_processor.decode_session_id(token)
