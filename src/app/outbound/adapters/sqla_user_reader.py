from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.queries.models.user import UserQm
from app.core.queries.ports.user_reader import ListUsersQm, UserReader
from app.core.queries.query_support.exceptions import SortingError
from app.core.queries.query_support.offset_pagination import OffsetPaginationParams
from app.core.queries.query_support.sorting import SortingOrder, SortingParams
from app.outbound.exceptions import ReaderError
from app.outbound.persistence_sqla.mappings.user import users_table


class SqlaUserReader(UserReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_users(
        self,
        *,
        pagination: OffsetPaginationParams,
        sorting: SortingParams,
    ) -> ListUsersQm:
        sorting_column = users_table.c.get(sorting.field)
        if sorting_column is None:
            raise SortingError(f"Invalid sorting field: '{sorting.field}'")
        order_by_expression = sorting_column.asc() if sorting.order == SortingOrder.ASC else sorting_column.desc()
        secondary_order_by = users_table.c.id.asc() if sorting.order == SortingOrder.ASC else users_table.c.id.desc()
        stmt = (
            select(
                users_table.c.id,
                users_table.c.username,
                users_table.c.role,
                users_table.c.is_active,
                users_table.c.created_at,
                users_table.c.updated_at,
                func.count().over().label("total"),
            )
            .order_by(order_by_expression, secondary_order_by)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        try:
            result = await self._session.execute(stmt)
            rows = result.all()
        except SQLAlchemyError as e:
            raise ReaderError from e
        if not rows:
            total_stmt = select(func.count()).select_from(users_table)
            try:
                total = int(await self._session.scalar(total_stmt) or 0)
            except SQLAlchemyError as e:
                raise ReaderError from e
            return ListUsersQm(
                users=[],
                total=total,
                limit=pagination.limit,
                offset=pagination.offset,
            )
        users = [
            UserQm(
                id=row.id,
                username=row.username,
                role=row.role,
                is_active=row.is_active,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
        return ListUsersQm(
            users=users,
            total=rows[0].total,
            limit=pagination.limit,
            offset=pagination.offset,
        )
