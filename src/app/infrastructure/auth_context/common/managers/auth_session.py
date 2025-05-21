import logging
from datetime import datetime, timedelta

from app.domain.entities.user.value_objects import UserId
from app.infrastructure.auth_context.common.auth_session import AuthSession
from app.infrastructure.auth_context.common.managers.jwt_token import JwtTokenManager
from app.infrastructure.auth_context.common.sqla_auth_session_data_mapper import (
    SqlaAuthSessionDataMapper,
)
from app.infrastructure.auth_context.common.str_auth_session_id_generator import (
    StrAuthSessionIdGenerator,
)
from app.infrastructure.auth_context.common.utc_auth_session_timer import (
    UtcAuthSessionTimer,
)
from app.infrastructure.exceptions.gateway_implementations import DataMapperError

log = logging.getLogger(__name__)


class AuthSessionManager:
    def __init__(
        self,
        str_auth_session_id_generator: StrAuthSessionIdGenerator,
        utc_auth_session_timer: UtcAuthSessionTimer,
        sqla_auth_session_data_mapper: SqlaAuthSessionDataMapper,
        jwt_token_manager: JwtTokenManager,
    ):
        self._str_auth_session_id_generator = str_auth_session_id_generator
        self._utc_auth_session_timer = utc_auth_session_timer
        self._sqla_auth_session_data_mapper = sqla_auth_session_data_mapper
        self._jwt_token_manager = jwt_token_manager

    def create_auth_session(self, user_id: UserId) -> AuthSession:
        log.debug("Create auth session: started. User id: '%s'.", user_id.value)

        auth_session_id: str = self._str_auth_session_id_generator()
        expiration: datetime = self._utc_auth_session_timer.access_expiration
        auth_session: AuthSession = AuthSession(
            id_=auth_session_id,
            user_id=user_id,
            expiration=expiration,
        )

        log.debug(
            "Create auth session: done. User id: '%s', Auth session id: '%s'.",
            user_id.value,
            auth_session.id_,
        )
        return auth_session

    def add_auth_session(self, auth_session: AuthSession) -> bool:
        log.debug("Add auth session: started. Auth session id: '%s'.", auth_session.id_)

        try:
            self._sqla_auth_session_data_mapper.add(auth_session)

        except DataMapperError as error:
            log.error(
                "Add auth session: failed. Auth session id: '%s'. Error: %s",
                auth_session.id_,
                error,
            )
            return False

        log.debug("Add auth session: done. Auth session id: '%s'.", auth_session.id_)
        return True

    async def get_auth_session(
        self,
        auth_session_id: str,
        for_update: bool = False,
    ) -> AuthSession | None:
        log.debug("Get auth session: started. Auth session id: '%s'.", auth_session_id)

        try:
            auth_session: AuthSession | None = (
                await self._sqla_auth_session_data_mapper.read(
                    auth_session_id, for_update=for_update
                )
            )

        except DataMapperError as error:
            log.error(
                "Get auth session: failed. Auth session id: '%s'. Error: %s",
                auth_session_id,
                error,
            )
            return None

        if auth_session is None:
            log.debug("Get auth session: done. No auth session id.")
            return None

        log.debug("Get auth session: done. Auth session id: '%s'.", auth_session.id_)
        return auth_session

    async def get_current_auth_session(self) -> AuthSession | None:
        log.debug("Get current auth session: started.")

        access_token: str | None = (
            self._jwt_token_manager.get_access_token_from_request()
        )
        if access_token is None:
            log.debug("Get current auth session: failed. No access token.")
            return None

        auth_session_id: str | None = (
            self._jwt_token_manager.get_auth_session_id_from_access_token(access_token)
        )
        if auth_session_id is None:
            log.debug("Get current auth session: failed. No auth session id in token.")
            return None

        auth_session: AuthSession | None = await self.get_auth_session(auth_session_id)
        if auth_session is None:
            log.debug("Get current auth session: done. No auth session id.")
            return None

        log.debug(
            "Get current auth session: done. Auth session id: '%s'.", auth_session.id_
        )
        return auth_session

    def is_auth_session_expired(self, auth_session: AuthSession) -> bool:
        log.debug(
            "Is auth session expired: started. Auth session id: %s.", auth_session.id_
        )

        is_expired: bool = (
            auth_session.expiration <= self._utc_auth_session_timer.current_time
        )

        log.debug(
            "Is auth session expired: done. Auth session id: %s.", auth_session.id_
        )
        return is_expired

    def is_auth_session_near_expiry(self, auth_session: AuthSession) -> bool:
        log.debug(
            "Is auth session near expiry: started. Auth session id: %s.",
            auth_session.id_,
        )

        time_remaining: timedelta = (
            auth_session.expiration - self._utc_auth_session_timer.current_time
        )
        is_near_expiry: bool = (
            time_remaining < self._utc_auth_session_timer.refresh_trigger_interval
        )

        log.debug(
            "Is auth session near expiry: done. Auth session id: %s.", auth_session.id_
        )
        return is_near_expiry

    def prolong_auth_session(self, auth_session: AuthSession) -> None:
        log.debug(
            "Prolong auth session: started. Auth session id: %s.", auth_session.id_
        )

        new_expiration: datetime = self._utc_auth_session_timer.access_expiration
        auth_session.expiration = new_expiration

        try:
            self._sqla_auth_session_data_mapper.add(auth_session)

        except DataMapperError as error:
            log.error(
                "Prolong auth session: failed. Auth session id: '%s'. Error: %s",
                auth_session.id_,
                error,
            )

        log.debug("Prolong auth session: done. Auth session id: %s.", auth_session.id_)

    async def delete_auth_session(self, auth_session_id: str) -> bool:
        log.debug(
            "Delete auth session: started. Auth session id: '%s'.", auth_session_id
        )

        try:
            is_deleted: bool = await self._sqla_auth_session_data_mapper.delete(
                auth_session_id
            )

        except DataMapperError as error:
            log.error(
                "Delete auth session: failed. Auth session id: '%s'. Error: %s",
                auth_session_id,
                error,
            )
            return False

        if not is_deleted:
            log.error(
                "Delete auth session: failed. Auth session not found, id: '%s'.",
                auth_session_id,
            )
            return False

        log.debug("Delete auth session: done. Auth session id: '%s'.", auth_session_id)
        return True
