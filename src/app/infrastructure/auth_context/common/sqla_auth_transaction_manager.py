import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.application.common.ports.transaction_manager import TransactionManager
from app.infrastructure.auth_context.common.new_types import AuthAsyncSession
from app.infrastructure.exceptions.gateway_implementations import DataMapperError

log = logging.getLogger(__name__)


class SqlaAuthTransactionManager(TransactionManager):
    def __init__(self, session: AuthAsyncSession):
        self._session = session

    async def flush(self) -> None:
        """
        :raises DataMapperError:
        """
        try:
            await self._session.flush()
            log.debug("Flush was done by Auth session.")

        except IntegrityError as error:
            raise DataMapperError("Database constraint violation.") from error

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, flush failed.") from error

    async def commit(self) -> None:
        """
        :raises DataMapperError:
        """
        try:
            await self._session.commit()
            log.debug("Commit was done by Auth session.")

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, commit failed.") from error
