from sqlalchemy import Select, exists, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.application.exceptions import DataGatewayError
from app.application.user_helpers.ports.user_data_gateway import UserDataGateway
from app.domain.user.value_objects import UserId, Username
from app.infrastructure.user.persistence_sqla import User


class SqlaUserDataMapper(UserDataGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        """
        :raises DataGatewayError:
        """
        try:
            self._session.add(user)
            await self._session.flush()

        except OSError as error:
            raise DataGatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed.") from error

    async def read_by_id(self, user_id: UserId) -> User | None:
        """
        :raises DataGatewayError:
        """
        select_stmt: Select = select(User).where(eq(User.id_, user_id))  # type: ignore

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return user

        except OSError as error:
            raise DataGatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed.") from error

    async def read_by_username(
        self, username: Username, for_update: bool = False
    ) -> User | None:
        """
        :raises DataGatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(
            eq(User.username, username),  # type: ignore
        )

        if for_update:
            select_stmt = select_stmt.with_for_update()

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return user

        except OSError as error:
            raise DataGatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed.") from error

    async def is_username_unique(self, username: Username) -> bool:
        """
        :raises DataGatewayError:
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
            raise DataGatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed.") from error

    async def read_all(self, limit: int, offset: int) -> list[User]:
        """
        :raises DataGatewayError:
        """
        select_stmt: Select[tuple[User]] = select(User).limit(limit).offset(offset)

        try:
            users: list[User] = list((await self._session.scalars(select_stmt)).all())

            return users

        except OSError as error:
            raise DataGatewayError("Connection failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed.") from error
