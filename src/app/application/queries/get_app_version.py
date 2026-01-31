import logging
from dataclasses import dataclass

from app.application.common.ports.app_version_provider import AppVersionProvider
from app.application.common.services.request_id import RequestIdService

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class AppVersionResult:
    version: str


class GetAppVersionQueryService:
    """
    - Open to everyone.
    - Returns current application version.
    """

    def __init__(
        self,
        version_provider: AppVersionProvider,
        request_id_service: RequestIdService,
    ) -> None:
        self._version_provider = version_provider
        self._request_id_service = request_id_service

    async def execute(self) -> AppVersionResult:
        request_id = self._request_id_service.get_current_request_id()
        log.debug("Get app version: request_id=%s", request_id)
        version = self._version_provider.get_version()
        return AppVersionResult(version=version)
