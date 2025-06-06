from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.domain.entities.user import User
from app.domain.value_objects.user_id import UserId
from app.domain.value_objects.username.username import Username
from app.infrastructure.adapters.application.new_types import UserAsyncSession
from app.infrastructure.exceptions.gateway_implementations import DataMapperError


class SqlaUserDataMapper(UserCommandGateway):
    def __init__(self, session: UserAsyncSession):
        self._session = session

    def add(self, user: User) -> None:
        """
        :raises DataMapperError:
        """
        try:
            self._session.add(user)

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read_by_id(self, user_id: UserId) -> User | None:
        """
        :raises DataMapperError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(User.id_ == user_id)  # type: ignore

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return user

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error

    async def read_by_username(
        self,
        username: Username,
        for_update: bool = False,
    ) -> User | None:
        """
        :raises DataMapperError:
        """
        select_stmt: Select[tuple[User]] = select(User).where(User.username == username)  # type: ignore

        if for_update:
            select_stmt = select_stmt.with_for_update()

        try:
            user: User | None = (
                await self._session.execute(select_stmt)
            ).scalar_one_or_none()

            return user

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed.") from error
