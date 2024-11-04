import logging
from datetime import datetime, timedelta

from app.application.committer import Committer
from app.application.user.data_gateways.session import SessionDataGateway
from app.application.user.exceptions import SessionExpired
from app.application.user.ports.session_id_generator import SessionIdGenerator
from app.application.user.ports.session_timer import SessionTimer
from app.application.user.record_session import SessionRecord
from app.application.user.services.token import TokenService
from app.domain.user.exceptions.non_existence import SessionNotFoundById
from app.domain.user.vo_user import UserId

log = logging.getLogger(__name__)


class SessionService:
    def __init__(
        self,
        session_id_generator: SessionIdGenerator,
        session_timer: SessionTimer,
        session_data_gateway: SessionDataGateway,
        committer: Committer,
        token_service: TokenService,
    ):
        self._session_id_generator = session_id_generator
        self._session_timer = session_timer
        self._session_data_gateway = session_data_gateway
        self._committer = committer
        self._token_service = token_service

    async def create_session(self, user_id: UserId) -> SessionRecord:
        log.debug("Create session: started. User id: '%s'.", user_id.value)

        session_id: str = self._session_id_generator()
        expiration: datetime = self._session_timer.access_expiration
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

    async def save_session(self, session_record: SessionRecord) -> None:
        """
        :raises DataGatewayError:
        """
        log.debug("Save session: started. Session id: '%s'.", session_record.id_)

        await self._session_data_gateway.save(session_record)

        await self._committer.commit()
        log.debug("Save session: done. Session id: '%s'.", session_record.id_)

    async def delete_session(self, session_id: str) -> None:
        """
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        """
        log.debug("Delete session: started. Session id: '%s'.", session_id)

        if not await self._session_data_gateway.delete(session_id):
            raise SessionNotFoundById(session_id)

        await self._committer.commit()
        log.debug("Delete session: done. Session id: '%s'.", session_id)

    async def delete_all_sessions_by_user_id(self, user_id: UserId) -> None:
        """
        :raises DataGatewayError:
        """
        log.debug(
            "Delete all sessions by user id: started. User id: '%s'.", user_id.value
        )

        await self._session_data_gateway.delete_all_for_user(user_id)

        await self._committer.commit()
        log.debug("Delete all sessions by user id: done. User id: '%s'.", user_id.value)

    def is_session_near_expiry(self, session: SessionRecord) -> bool:
        log.debug("Is session near expiry: started. Session id: %s.", session.id_)

        time_remaining: timedelta = (
            session.expiration - self._session_timer.current_time
        )

        log.debug("Is session near expiry: done. Session id: %s.", session.id_)
        return time_remaining < self._session_timer.refresh_trigger_interval

    async def prolong_session(self, session: SessionRecord) -> None:
        """
        :raises DataGatewayError:
        """
        log.debug("Prolong session: started. Session id: %s.", session.id_)

        new_expiration: datetime = self._session_timer.access_expiration
        session.expiration = new_expiration

        await self._session_data_gateway.save(session)

        await self._committer.commit()
        log.debug("Prolong session: done. Session id: %s.", session.id_)

    async def get_current_session(self) -> SessionRecord:
        """
        :raises AdapterError:
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        :raises SessionExpired:
        """
        log.debug("Get current session: started.")

        access_token: str = self._token_service.get_access_token_from_request()
        session_id: str = self._token_service.get_session_id_from_access_token(
            access_token
        )

        session: SessionRecord = await self._get_session(session_id)
        self._check_session_expiration(session)

        log.debug("Get current session: done. Session id: '%s'.", session.id_)
        return session

    async def _get_session(
        self, session_id: str, for_update: bool = False
    ) -> SessionRecord:
        """
        :raises DataGatewayError:
        :raises SessionNotFoundById:
        """
        log.debug("Get session: started. Session id: '%s'.", session_id)

        session: SessionRecord | None = await self._session_data_gateway.read(
            session_id, for_update=for_update
        )

        if session is None:
            raise SessionNotFoundById(session_id)

        log.debug("Get session: done. Session id: '%s'.", session.id_)
        return session

    def _check_session_expiration(self, session: SessionRecord) -> None:
        """
        :raises SessionExpired:
        """
        log.debug("Check session expiration: started. Session id: %s.", session.id_)

        if session.expiration <= self._session_timer.current_time:
            raise SessionExpired(session.id_)

        log.debug("Check session expiration: done. Session id: %s.", session.id_)
