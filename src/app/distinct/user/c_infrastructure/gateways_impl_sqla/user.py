from sqlalchemy import Select, exists, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.common.b_application.exceptions import GatewayError
from app.distinct.user.a_domain.entity_user import User
from app.distinct.user.a_domain.exceptions.non_existence import (
    UserNotFoundById,
    UserNotFoundByUsername,
)
from app.distinct.user.a_domain.vo_user import UserId, Username
from app.distinct.user.b_application.gateways.user import UserGateway


class SqlaUserGateway(UserGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> None:
        """
        :raises GatewayError:
        """
        try:
            self._session.add(user)
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def read_by_id(self, user_id: UserId) -> User:
        """
        :raises UserNotFoundById:
        :raises GatewayError:
        """
        select_stmt: Select = select(User).where(eq(User.id_, user_id))  # type: ignore

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if user is not None:
                return user
            raise UserNotFoundById(user_id)

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def read_by_username(self, username: Username) -> User:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(
            eq(User.username, username),  # type: ignore
        )

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if user is not None:
                return user
            raise UserNotFoundByUsername(username.value)

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def is_username_unique(self, username: Username) -> bool:
        """
        :raises GatewayError:
        """
        select_exists_stmt: Select[tuple[bool]] = select(
            exists().where(eq(User.username, username)),  # type: ignore
        )

        try:
            username_exists: bool = (
                await self._session.scalar(select_exists_stmt) or False
            )
            return not username_exists

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def get_all(self, limit: int, offset: int) -> list[User]:
        """
        :raises GatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).limit(limit).offset(offset)

        try:
            users: list[User] = list((await self._session.scalars(select_stmt)).all())
            return users

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def set_activation_status_by_username(
        self, username: Username, is_active: bool
    ) -> None:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(
            eq(User.username, username),  # type: ignore
        )

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if user is None:
                raise UserNotFoundByUsername(username.value)

            (user.activate if is_active else user.inactivate)()
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error

    async def set_admin_status_by_username(
        self, username: Username, is_admin: bool
    ) -> None:
        """
        :raises UserNotFoundByUsername:
        :raises GatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(
            eq(User.username, username),  # type: ignore
        )

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            if user is None:
                raise UserNotFoundByUsername(username.value)

            (user.grant_admin if is_admin else user.revoke_admin)()
            await self._session.flush()

        except OSError as error:
            raise GatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed.") from error
