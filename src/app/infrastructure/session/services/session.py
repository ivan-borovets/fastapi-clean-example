import logging
from datetime import datetime, timedelta

from app.domain.user.value_objects import UserId
from app.infrastructure.exceptions import DataMapperError
from app.infrastructure.persistence.sqla.committer import SqlaCommitter
from app.infrastructure.record_session import SessionRecord
from app.infrastructure.session.services.jwt_token import JwtTokenService
from app.infrastructure.session.session_data_mapper_sqla import SqlaSessionDataMapper
from app.infrastructure.session.session_id_generator_str import StrSessionIdGenerator
from app.infrastructure.session.session_timer_utc import UtcSessionTimer

log = logging.getLogger(__name__)


class SessionService:
    def __init__(
        self,
        str_session_id_generator: StrSessionIdGenerator,
        utc_session_timer: UtcSessionTimer,
        sqla_session_data_mapper: SqlaSessionDataMapper,
        sqla_committer: SqlaCommitter,
        jwt_token_service: JwtTokenService,
    ):
        self._str_session_id_generator = str_session_id_generator
        self._utc_session_timer = utc_session_timer
        self._sqla_session_data_mapper = sqla_session_data_mapper
        self._sqla_committer = sqla_committer
        self._jwt_token_service = jwt_token_service

    async def create_session(self, user_id: UserId) -> SessionRecord:
        log.debug("Create session: started. User id: '%s'.", user_id.value)

        session_id: str = self._str_session_id_generator()
        expiration: datetime = self._utc_session_timer.access_expiration
        session_record: SessionRecord = SessionRecord(
            id_=session_id,
            user_id=user_id,
            expiration=expiration,
        )

        log.debug(
            "Create session: done. User id: '%s', Session id: '%s'.",
            user_id.value,
            session_record.id_,
        )
        return session_record

    async def save_session(self, session_record: SessionRecord) -> bool:
        log.debug("Save session: started. Session id: '%s'.", session_record.id_)

        try:
            await self._sqla_session_data_mapper.save(session_record)
            await self._sqla_committer.commit()

        except DataMapperError as error:
            log.error(
                "Save session: failed. Session id: '%s'. Error: %s",
                session_record.id_,
                error,
            )
            return False

        log.debug("Save session: done. Session id: '%s'.", session_record.id_)
        return True

    async def get_session(
        self,
        session_id: str,
        for_update: bool = False,
    ) -> SessionRecord | None:
        log.debug("Get session: started. Session id: '%s'.", session_id)

        try:
            session: SessionRecord | None = await self._sqla_session_data_mapper.read(
                session_id, for_update=for_update
            )

        except DataMapperError as error:
            log.error(
                "Get session: failed. Session id: '%s'. Error: %s",
                session_id,
                error,
            )
            return None

        if session is None:
            log.debug("Get session: done. No session id.")
            return None

        log.debug("Get session: done. Session id: '%s'.", session.id_)
        return session

    async def get_current_session(self) -> SessionRecord | None:
        log.debug("Get current session: started.")

        access_token: str | None = (
            self._jwt_token_service.get_access_token_from_request()
        )
        if access_token is None:
            log.debug("Get current session: failed. No access token.")
            return None

        session_id: str | None = (
            self._jwt_token_service.get_session_id_from_access_token(access_token)
        )
        if session_id is None:
            log.debug("Get current session: failed. No session id in token.")
            return None

        session: SessionRecord | None = await self.get_session(session_id)
        if session is None:
            log.debug("Get current session: done. No session id.")
            return None

        log.debug("Get current session: done. Session id: '%s'.", session.id_)
        return session

    def is_session_expired(self, session: SessionRecord) -> bool:
        log.debug("Is session expired: started. Session id: %s.", session.id_)

        is_expired: bool = session.expiration <= self._utc_session_timer.current_time

        log.debug("Is session expired: done. Session id: %s.", session.id_)
        return is_expired

    def is_session_near_expiry(self, session: SessionRecord) -> bool:
        log.debug("Is session near expiry: started. Session id: %s.", session.id_)

        time_remaining: timedelta = (
            session.expiration - self._utc_session_timer.current_time
        )
        is_near_expiry: bool = (
            time_remaining < self._utc_session_timer.refresh_trigger_interval
        )

        log.debug("Is session near expiry: done. Session id: %s.", session.id_)
        return is_near_expiry

    async def prolong_session(self, session: SessionRecord) -> None:
        log.debug("Prolong session: started. Session id: %s.", session.id_)

        new_expiration: datetime = self._utc_session_timer.access_expiration
        session.expiration = new_expiration

        try:
            await self._sqla_session_data_mapper.save(session)
            await self._sqla_committer.commit()

        except DataMapperError as error:
            log.error(
                "Prolong session: failed. Session id: '%s'. Error: %s",
                session.id_,
                error,
            )
            return None

        log.debug("Prolong session: done. Session id: %s.", session.id_)

    async def delete_session(self, session_id: str) -> bool:
        log.debug("Delete session: started. Session id: '%s'.", session_id)

        try:
            is_deleted: bool = await self._sqla_session_data_mapper.delete(session_id)
            await self._sqla_committer.commit()

        except DataMapperError as error:
            log.error(
                "Delete session: failed. Session id: '%s'. Error: %s",
                session_id,
                error,
            )
            return False

        if not is_deleted:
            log.error(
                "Delete session: failed. Session not found, id: '%s'.", session_id
            )
            return False

        log.debug("Delete session: done. Session id: '%s'.", session_id)
        return True
