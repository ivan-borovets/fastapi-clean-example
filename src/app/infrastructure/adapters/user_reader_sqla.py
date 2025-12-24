import logging

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.exceptions.query import SortingError
from app.application.common.ports.user_query_gateway import (
    ListUsersQM,
    UserQueryGateway,
    UserQueryModel,
)
from app.application.common.query_params.offset_pagination import OffsetPaginationParams
from app.application.common.query_params.sorting import SortingOrder, SortingParams
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import ReaderError
from app.infrastructure.persistence_sqla.mappings.user import users_table

log = logging.getLogger(__name__)


class SqlaUserReader(UserQueryGateway):
    def __init__(self, session: MainAsyncSession) -> None:
        self._session = session

    async def read_all(
        self,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQM:
        """
        :raises SortingError:
        :raises ReaderError:
        """
        sorting_col = users_table.c.get(sorting.field)
        if sorting_col is None:
            raise SortingError(f"Invalid sorting field: '{sorting.field}'")

        order_by = (
            sorting_col.asc()
            if sorting.order == SortingOrder.ASC
            else sorting_col.desc()
        )

        stmt = (
            select(
                users_table.c.id,
                users_table.c.username,
                users_table.c.role,
                users_table.c.is_active,
                func.count().over().label("total"),
            )
            .order_by(order_by)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )

        try:
            result = await self._session.execute(stmt)
            rows = result.all()
        except SQLAlchemyError as err:
            raise ReaderError(DB_QUERY_FAILED) from err

        if not rows:
            return ListUsersQM(users=[], total=0)

        users = [
            UserQueryModel(
                id_=row.id,
                username=row.username,
                role=row.role,
                is_active=row.is_active,
            )
            for row in rows
        ]
        total = rows[0].total
        return ListUsersQM(users=users, total=total)
