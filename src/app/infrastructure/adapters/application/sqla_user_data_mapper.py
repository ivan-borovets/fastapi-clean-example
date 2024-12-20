from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import eq

from app.application.common.ports.user_data_gateway import UserDataGateway
from app.domain.entities.user.value_objects import UserId, Username
from app.domain.exceptions.user.existence import UsernameAlreadyExists
from app.infrastructure.exceptions.data_mapper import DataMapperError
from app.infrastructure.sqla_persistence.mappings.user import User


class SqlaUserDataMapper(UserDataGateway):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        """
        :raises UsernameAlreadyExists:
        :raises DataMapperError:
        """
        try:
            self._session.add(user)
            await self._session.flush()

        except IntegrityError as error:
            raise UsernameAlreadyExists(user.username.value) from error
        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read_by_id(self, user_id: UserId) -> User | None:
        """
        :raises DataMapperError:
        """
        select_stmt: Select = select(User).where(eq(User.id_, user_id))  # type: ignore

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return user

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read_by_username(
        self, username: Username, for_update: bool = False
    ) -> User | None:
        """
        :raises DataMapperError:
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

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read_all(self, limit: int, offset: int) -> list[User]:
        """
        :raises DataMapperError:
        """
        select_stmt: Select[tuple[User]] = select(User).limit(limit).offset(offset)

        try:
            users: list[User] = list((await self._session.scalars(select_stmt)).all())

            return users

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error
