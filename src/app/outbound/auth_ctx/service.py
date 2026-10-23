from app.core.common.entities.types_ import UserId
from app.outbound.auth_ctx.cookie_manager import CookieManager
from app.outbound.auth_ctx.exceptions import AuthenticationError
from app.outbound.auth_ctx.id_factory import create_session_id
from app.outbound.auth_ctx.jwt_processor import JwtProcessor
from app.outbound.auth_ctx.model import AuthSession, SessionId
from app.outbound.auth_ctx.session_expiry_policy import AuthSessionExpiryPolicy
from app.outbound.auth_ctx.sqla_transaction_manager import AuthSqlaTransactionManager
from app.outbound.auth_ctx.sqla_tx_storage import AuthSessionSqlaTxStorage
from app.outbound.auth_ctx.utc_clock import AuthUtcClock


class AuthService:
    def __init__(
        self,
        utc_clock: AuthUtcClock,
        session_expiry_policy: AuthSessionExpiryPolicy,
        session_tx_storage: AuthSessionSqlaTxStorage,
        transaction_manager: AuthSqlaTransactionManager,
        jwt_processor: JwtProcessor,
        cookie_manager: CookieManager,
    ) -> None:
        self._utc_clock = utc_clock
        self._session_expiry_policy = session_expiry_policy
        self._session_tx_storage = session_tx_storage
        self._transaction_manager = transaction_manager
        self._jwt_processor = jwt_processor
        self._cookie_manager = cookie_manager

    async def issue_session(self, user_id: UserId) -> None:
        session = AuthSession(
            id_=create_session_id(),
            user_id=user_id,
            expiration=self._session_expiry_policy.expiration_from(self._utc_clock.now),
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
        await self._transaction_manager.commit()
        if session is None:
            raise AuthenticationError

        now = self._utc_clock.now
        if self._session_expiry_policy.is_expired(session, now=now):
            raise AuthenticationError

        if self._session_expiry_policy.needs_refresh(session, now=now):
            session.expiration = self._session_expiry_policy.expiration_from(now)
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
