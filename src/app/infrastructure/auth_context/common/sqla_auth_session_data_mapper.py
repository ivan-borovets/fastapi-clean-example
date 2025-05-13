from sqlalchemy import Delete, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.dml import ReturningDelete
from sqlalchemy.sql.operators import eq

from app.domain.entities.user.value_objects import UserId
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.auth_context.common.new_types import AuthAsyncSession
from app.infrastructure.exceptions.gateway_implementations import DataMapperError


class SqlaAuthSessionDataMapper:
    def __init__(self, session: AuthAsyncSession):
        self._session = session

    async def add(self, auth_session: AuthSession) -> None:
        """
        :raises DataMapperError:
        """
        try:
            self._session.add(auth_session)

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read(
        self, auth_session_id: str, for_update: bool = False
    ) -> AuthSession | None:
        """
        :raises DataMapperError:
        """
        try:
            auth_session: AuthSession | None = await self._session.get(
                AuthSession,
                auth_session_id,
                with_for_update=for_update,
            )

            return auth_session

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def delete(self, auth_session_id: str) -> bool:
        """
        :raises DataMapperError:
        """
        delete_stmt: ReturningDelete[tuple[str, ...]] = (
            delete(AuthSession)
            .where(eq(AuthSession.id_, auth_session_id))  # type: ignore
            .returning(AuthSession.id_)
        )

        try:
            result = await self._session.execute(delete_stmt)

            deleted_ids: tuple[str, ...] = tuple(result.scalars().all())

            return bool(deleted_ids)

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def delete_all_for_user(self, user_id: UserId) -> None:
        """
        :raises DataMapperError:
        """
        delete_stmt: Delete = delete(AuthSession).where(
            eq(AuthSession.user_id, user_id)  # type: ignore
        )

        try:
            await self._session.execute(delete_stmt)

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error
