import logging
from collections.abc import Mapping
from typing import Any, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.common.ports.transaction_manager import TransactionManager
from app.domain.exceptions.user import UsernameAlreadyExists
from app.infrastructure.adapters.application.new_types import UserAsyncSession
from app.infrastructure.exceptions.gateway_implementations import DataMapperError

log = logging.getLogger(__name__)


class SqlaUserTransactionManager(TransactionManager):
    def __init__(self, session: UserAsyncSession):
        self._session = session

    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
        try:
            await self._session.flush()
            log.debug("Flush was done by User session.")

        except IntegrityError as error:
            if "uq_users_username" in str(error):
                params: Mapping[str, Any] = cast("Mapping[str, Any]", error.params)
                username = str(params.get("username", "unknown"))
                raise UsernameAlreadyExists(username) from error

            raise DataMapperError("Database constraint violation.") from error

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, flush failed.") from error

    async def commit(self) -> None:
        """
        :raises DataMapperError:
        """
        try:
            await self._session.commit()
            log.debug("Commit was done by User session.")

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, commit failed.") from error
