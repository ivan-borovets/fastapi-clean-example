import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.ports.committer import Committer
from app.infrastructure.exceptions.data_mapper import DataMapperError

log = logging.getLogger(__name__)


class SqlaCommitter(Committer):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        """
        :raises DataMapperError:
        """
        try:
            await self._session.commit()
            log.debug("Commit was done by session with info: '%s'.", self._session.info)

        except OSError as error:
            raise DataMapperError("Connection failed, commit failed.") from error
        except SQLAlchemyError as error:
            raise DataMapperError("Database query failed, commit failed.") from error
