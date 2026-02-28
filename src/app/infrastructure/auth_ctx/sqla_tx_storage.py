from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError

from app.core.common.entities.types_ import UserId
from app.infrastructure.auth_ctx.model import AuthSession, SessionId
from app.infrastructure.auth_ctx.types_ import AuthAsyncSession
from app.infrastructure.exceptions import StorageError
from app.infrastructure.persistence_sqla.mappings.auth_session import auth_sessions_table


class AuthSessionSqlaTxStorage:
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    def add(self, auth_session: AuthSession) -> None:
        try:
            self._session.add(auth_session)
        except SQLAlchemyError as e:
            raise StorageError from e

    async def get_by_id(
        self,
        session_id: SessionId,
        *,
        for_update: bool = False,
    ) -> AuthSession | None:
        try:
            return await self._session.get(
                AuthSession,
                session_id,
                with_for_update=for_update,
            )
        except SQLAlchemyError as e:
            raise StorageError from e

    async def update(self, auth_session: AuthSession) -> None:
        try:
            await self._session.merge(auth_session)
        except SQLAlchemyError as e:
            raise StorageError from e

    async def delete(self, session_id: SessionId) -> None:
        stmt = delete(auth_sessions_table).where(auth_sessions_table.c.id == session_id)
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as e:
            raise StorageError from e

    async def delete_all_for_user(self, user_id: UserId) -> None:
        stmt = delete(auth_sessions_table).where(auth_sessions_table.c.user_id == user_id)
        try:
            await self._session.execute(stmt)
        except SQLAlchemyError as e:
            raise StorageError from e
