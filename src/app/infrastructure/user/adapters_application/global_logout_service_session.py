import logging

from app.application.user.ports.global_logout_service import GlobalLogoutService
from app.domain.user.value_objects import UserId
from app.infrastructure.persistence.sqla.committer import SqlaCommitter
from app.infrastructure.session.session_data_mapper_sqla import SqlaSessionDataMapper

log = logging.getLogger(__name__)


class SessionGlobalLogoutService(GlobalLogoutService):
    def __init__(
        self,
        sqla_session_data_mapper: SqlaSessionDataMapper,
        sqla_committer: SqlaCommitter,
    ):
        self._sqla_session_data_mapper = sqla_session_data_mapper
        self._sqla_committer = sqla_committer

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """
        :raises DataGatewayError:
        """

        log.debug("Remove all user access: started. User id: '%s'.", user_id.value)

        await self._sqla_session_data_mapper.delete_all_for_user(user_id)

        await self._sqla_committer.commit()
        log.debug("Remove all user access: done. User id: '%s'.", user_id.value)
