import logging
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import ColumnElement, Result, Row, Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.user_query_gateway import UserQueryGateway
from app.application.common.query_models.user import UserQueryModel
from app.application.common.query_params.sorting import SortingOrder
from app.application.common.query_params.user import UserListParams
from app.domain.enums.user_role import UserRole
from app.infrastructure.adapters.constants import DB_QUERY_FAILED
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import ReaderError
from app.infrastructure.persistence_sqla.mappings.user import users_table

log = logging.getLogger(__name__)


class SqlaUserReader(UserQueryGateway):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    async def read_all(
        self,
        user_read_all_params: UserListParams,
    ) -> list[UserQueryModel] | None:
        """
        :raises ReaderError:
        """
        table_sorting_field: ColumnElement[UUID | str | UserRole | bool] | None = (
            users_table.c.get(user_read_all_params.sorting.sorting_field)
        )
        if table_sorting_field is None:
            log.error(
                "Invalid sorting field: '%s'.",
                user_read_all_params.sorting.sorting_field,
            )
            return None

        order_by: ColumnElement[UUID | str | UserRole | bool] = (
            table_sorting_field.asc()
            if user_read_all_params.sorting.sorting_order == SortingOrder.ASC
            else table_sorting_field.desc()
        )

        select_stmt: Select[tuple[UUID, str, UserRole, bool]] = (
            select(
                users_table.c.id,
                users_table.c.username,
                users_table.c.role,
                users_table.c.is_active,
            )
            .order_by(order_by)
            .limit(user_read_all_params.pagination.limit)
            .offset(user_read_all_params.pagination.offset)
        )

        try:
            result: Result[
                tuple[UUID, str, UserRole, bool]
            ] = await self._session.execute(select_stmt)
            rows: Sequence[Row[tuple[UUID, str, UserRole, bool]]] = result.all()

            return [
                UserQueryModel(
                    id_=row.id,
                    username=row.username,
                    role=row.role,
                    is_active=row.is_active,
                )
                for row in rows
            ]

        except SQLAlchemyError as error:
            raise ReaderError(DB_QUERY_FAILED) from error
