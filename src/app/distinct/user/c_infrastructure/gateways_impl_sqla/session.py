from datetime import datetime

from sqlalchemy import Delete, Select, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.common.b_application.exceptions import GatewayError
from app.distinct.user.a_domain.entity_session import Session
from app.distinct.user.a_domain.exceptions.non_existence import SessionNotFoundById
from app.distinct.user.a_domain.vo_session import SessionId
from app.distinct.user.a_domain.vo_user import UserId
from app.distinct.user.b_application.gateways.session import SessionGateway


class SqlaSessionGateway(SessionGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, session: Session) -> None:
        """
        :raises GatewayError:
        """
        try:
            self._session.add(session)
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def read_by_id(self, session_id: SessionId) -> Session:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[Session]] = select(Session).where(
            eq(Session.id_, session_id),  # type: ignore
        )

        try:
            session: Session | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if session is not None:
                return session
            raise SessionNotFoundById(session_id.value)

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def update_expiration_by_id(
        self, session_id: SessionId, new_expiration: datetime
    ) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[Session]] = select(Session).where(
            eq(Session.id_, session_id),  # type: ignore
        )

        try:
            existing_session: Session | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if existing_session is None:
                raise SessionNotFoundById(session_id.value)

            existing_session.extend(new_expiration)
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def delete_by_id(self, session_id: SessionId) -> None:
        """
        :raises SessionNotFoundById:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[Session]] = select(Session).where(
            eq(Session.id_, session_id),  # type: ignore
        )

        try:
            session: Session | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if session is None:
                raise SessionNotFoundById(session_id.value)

            await self._session.delete(session)

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def delete_all_of_user_id(self, user_id: UserId) -> None:
        """
        :raises GatewayError:
        """
        delete_stmt: Delete = delete(Session).where(
            eq(Session.user_id, user_id)  # type: ignore
        )

        try:
            await self._session.execute(delete_stmt)
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error
