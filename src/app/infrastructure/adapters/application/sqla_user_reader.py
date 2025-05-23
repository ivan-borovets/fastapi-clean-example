import logging
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import ColumnElement, Result, Row, Select, select
from sqlalchemy.exc import SQLAlchemyError

from app.application.common.ports.query_gateways.user import UserQueryGateway
from app.application.common.query_filters.sorting_order_enum import SortingOrderEnum
from app.application.common.query_filters.user.read_all import UserReadAllParams
from app.application.common.query_models.user import UserQueryModel
from app.domain.entities.user.role_enum import UserRoleEnum
from app.infrastructure.adapters.application.new_types import UserAsyncSession
from app.infrastructure.exceptions.gateway_implementations import ReaderError
from app.infrastructure.sqla_persistence.mappings.user import users_table

log = logging.getLogger(__name__)


class SqlaUserReader(UserQueryGateway):
    def __init__(self, session: UserAsyncSession):
        self._session = session

    async def read_all(
        self,
        user_read_all_params: UserReadAllParams,
    ) -> list[UserQueryModel] | None:
        """
        :raises ReaderError:
        """
        table_sorting_field: ColumnElement[UUID | str | UserRoleEnum | bool] | None = (
            users_table.c.get(user_read_all_params.sorting.sorting_field)
        )
        if table_sorting_field is None:
            log.error(
                "Invalid sorting field: '%s'.",
                user_read_all_params.sorting.sorting_field,
            )
            return None

        order_by: ColumnElement[UUID | str | UserRoleEnum | bool] = (
            table_sorting_field.asc()
            if user_read_all_params.sorting.sorting_order == SortingOrderEnum.ASC
            else table_sorting_field.desc()
        )

        select_stmt: Select[tuple[UUID, str, UserRoleEnum, bool]] = (
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
                tuple[UUID, str, UserRoleEnum, bool]
            ] = await self._session.execute(select_stmt)
            rows: Sequence[Row[tuple[UUID, str, UserRoleEnum, bool]]] = result.all()

            users: list[UserQueryModel] = [
                UserQueryModel(
                    id_=row.id,
                    username=row.username,
                    role=row.role,
                    is_active=row.is_active,
                )
                for row in rows
            ]

            return users

        except SQLAlchemyError as error:
            raise ReaderError("Database query failed.") from error
