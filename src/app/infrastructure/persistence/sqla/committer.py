import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.committer import Committer
from app.application.exceptions import DataGatewayError

log = logging.getLogger(__name__)


class SqlaCommitter(Committer):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        """
        :raises DataGatewayError:
        """
        try:
            await self._session.commit()
            log.debug("Commit was done by session with info: '%s'.", self._session.info)

        except OSError as error:
            raise DataGatewayError("Connection failed, commit failed.") from error
        except SQLAlchemyError as error:
            raise DataGatewayError("Database query failed, commit failed.") from error
