from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.b_application.exceptions import GatewayError
from app.common.b_application.persistence.committer import Committer


class SqlaCommitter(Committer):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        """
        :raises GatewayError:
        """
        try:
            await self._session.commit()

        except OSError as error:
            raise GatewayError("Connection failed, commit failed.") from error
        except SQLAlchemyError as error:
            raise GatewayError("Database query failed, commit failed.") from error
