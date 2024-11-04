import logging

from app.application.common.ports.access_revoker import AccessRevoker
from app.domain.user.value_objects import UserId
from app.infrastructure.adapters.application.sqla_committer import SqlaCommitter
from app.infrastructure.session_context.common.sqla_session_data_mapper import (
    SqlaSessionDataMapper,
)

log = logging.getLogger(__name__)


class SessionAccessRevoker(AccessRevoker):
    def __init__(
        self,
        sqla_session_data_mapper: SqlaSessionDataMapper,
        sqla_committer: SqlaCommitter,
    ):
        self._sqla_session_data_mapper = sqla_session_data_mapper
        self._sqla_committer = sqla_committer

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """
        :raises DataMapperError:
        """
        log.debug("Remove all user access: started. User id: '%s'.", user_id.value)

        await self._sqla_session_data_mapper.delete_all_for_user(user_id)

        await self._sqla_committer.commit()
        log.debug("Remove all user access: done. User id: '%s'.", user_id.value)
