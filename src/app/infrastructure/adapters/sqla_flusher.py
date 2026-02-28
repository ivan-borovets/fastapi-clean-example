import logging
from collections.abc import Mapping
from typing import Final

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.commands.exceptions import UsernameAlreadyExistsError
from app.core.commands.ports.flusher import Flusher
from app.infrastructure.exceptions import StorageError
from app.infrastructure.persistence_sqla import constraint_names as cn

logger = logging.getLogger(__name__)

DB_CONSTRAINT_VIOLATION: Final[str] = "Database constraint violation."
DB_FLUSH_DONE: Final[str] = "Flush was done."
DB_FLUSH_FAILED: Final[str] = "Flush failed."

CONSTRAINT_TO_ERROR: Final[Mapping[str, type[Exception]]] = {
    cn.UQ_USERS_USERNAME: UsernameAlreadyExistsError,
}


class SqlaFlusher(Flusher):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def flush(self) -> None:
        try:
            await self._session.flush()
            logger.debug("%s.", DB_FLUSH_DONE)

        except IntegrityError as e:
            msg = str(e)
            for name, exc_type in CONSTRAINT_TO_ERROR.items():
                if name in msg:
                    raise exc_type from e

            logger.warning("Unhandled integrity error: %s", msg)
            raise StorageError(DB_CONSTRAINT_VIOLATION) from e

        except SQLAlchemyError as e:
            raise StorageError(DB_FLUSH_FAILED) from e
