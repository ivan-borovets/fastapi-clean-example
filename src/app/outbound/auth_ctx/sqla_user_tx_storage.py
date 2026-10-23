from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.common.entities.user import User
from app.core.common.value_objects.username import Username
from app.outbound.auth_ctx.types_ import AuthAsyncSession
from app.outbound.exceptions import StorageError
from app.outbound.persistence_sqla.mappings.user import users_table


class AuthSqlaUserTxStorage:
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    async def get_by_username(
        self,
        username: Username,
        *,
        for_update: bool = False,
    ) -> User | None:
        stmt = select(User).where(users_table.c.username == username.value)
        if for_update:
            stmt = stmt.with_for_update()
        try:
            result = await self._session.execute(stmt)
        except SQLAlchemyError as e:
            raise StorageError from e
        return result.scalar_one_or_none()
