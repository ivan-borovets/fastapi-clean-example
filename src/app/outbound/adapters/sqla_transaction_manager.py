import logging
from typing import Final

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.commands.ports.transaction_manager import TransactionManager
from app.outbound.exceptions import StorageError

DB_COMMIT_DONE: Final[str] = "Commit was done."
DB_COMMIT_FAILED: Final[str] = "Commit failed."

logger = logging.getLogger(__name__)


class SqlaTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        try:
            await self._session.commit()
            logger.debug("%s.", DB_COMMIT_DONE)

        except SQLAlchemyError as e:
            raise StorageError(DB_COMMIT_FAILED) from e
