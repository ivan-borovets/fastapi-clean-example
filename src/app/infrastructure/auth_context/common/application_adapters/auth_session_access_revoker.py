import logging

from app.application.common.ports.access_revoker import AccessRevoker
from app.domain.value_objects.user_id import UserId
from app.infrastructure.auth_context.common.sqla_auth_session_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.infrastructure.auth_context.common.sqla_auth_transaction_manager import (
    SqlaAuthTransactionManager,
)

log = logging.getLogger(__name__)


class AuthSessionAccessRevoker(AccessRevoker):
    def __init__(
        self,
        sqla_auth_session_data_mapper: SqlaAuthSessionDataMapper,
        sqla_auth_transaction_manager: SqlaAuthTransactionManager,
    ):
        self._sqla_auth_session_data_mapper = sqla_auth_session_data_mapper
        self._sqla_auth_transaction_manager = sqla_auth_transaction_manager

    async def remove_all_user_access(self, user_id: UserId) -> None:
        """
        :raises DataMapperError:
        """
        log.debug("Remove all user access: started. User id: '%s'.", user_id.value)

        await self._sqla_auth_session_data_mapper.delete_all_for_user(user_id)

        await self._sqla_auth_transaction_manager.commit()
        log.debug("Remove all user access: done. User id: '%s'.", user_id.value)
