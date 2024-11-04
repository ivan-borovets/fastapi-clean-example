import logging
from typing import Any, Mapping, cast

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.ports.transaction_manager import TransactionManager
from app.domain.exceptions.user.existence import UsernameAlreadyExists
from app.infrastructure.exceptions.gateway_implementations import DataMapperError

log = logging.getLogger(__name__)


class SqlaTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def flush(self) -> None:
        """
        :raises DataMapperError:
        :raises UsernameAlreadyExists:
        """
        try:
            await self._session.flush()
            log.debug("Flush was done by session with info: '%s'.", self._session.info)

        except IntegrityError as error:
            if "uq_users_username" in str(error):
                params: Mapping[str, Any] = cast(Mapping[str, Any], error.params)
                username: str = str(params.get("username", "unknown"))
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
            log.debug("Commit was done by session with info: '%s'.", self._session.info)

        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, commit failed.") from error
