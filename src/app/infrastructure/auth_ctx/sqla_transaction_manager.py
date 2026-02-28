import logging
from typing import Final

from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.auth_ctx.types_ import AuthAsyncSession
from app.infrastructure.exceptions import StorageError

DB_COMMIT_DONE: Final[str] = "Commit was done."
DB_COMMIT_FAILED: Final[str] = "Commit failed."

logger = logging.getLogger(__name__)


class AuthSqlaTransactionManager:
    def __init__(self, session: AuthAsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        try:
            await self._session.commit()
            logger.debug("%s.", DB_COMMIT_DONE)

        except SQLAlchemyError as e:
            raise StorageError(DB_COMMIT_FAILED) from e
