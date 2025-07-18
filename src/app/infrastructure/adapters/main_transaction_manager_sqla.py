import logging
from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.common.ports.transaction_manager import (
    TransactionManager,
)
from app.domain.exceptions.user import UsernameAlreadyExistsError
from app.infrastructure.adapters.constants import (
    DB_COMMIT_DONE,
    DB_COMMIT_FAILED,
    DB_CONSTRAINT_VIOLATION,
    DB_FLUSH_DONE,
    DB_FLUSH_FAILED,
    DB_QUERY_FAILED,
)
from app.infrastructure.adapters.types import MainAsyncSession
from app.infrastructure.exceptions.gateway import DataMapperError

log = logging.getLogger(__name__)


class SqlaMainTransactionManager(TransactionManager):
    def __init__(self, session: MainAsyncSession):
        self._session = session

    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
        try:
            await self._session.flush()
            log.debug("%s Main session.", DB_FLUSH_DONE)

        except IntegrityError as error:
            if "uq_users_username" in str(error):
                params: Mapping[str, Any] = cast(Mapping[str, Any], error.params)
                username = str(params.get("username", "unknown"))
                raise UsernameAlreadyExistsError(username) from error

            raise DataMapperError(DB_CONSTRAINT_VIOLATION) from error

        except SQLAlchemyError as error:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_FLUSH_FAILED}") from error

    async def commit(self) -> None:
        """
        :raises DataMapperError:
        """
        try:
            await self._session.commit()
            log.debug("%s Main session.", DB_COMMIT_DONE)

        except SQLAlchemyError as error:
            raise DataMapperError(f"{DB_QUERY_FAILED} {DB_COMMIT_FAILED}") from error
