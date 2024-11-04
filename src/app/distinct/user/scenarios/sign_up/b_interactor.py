import logging

from app.base.b_application.interactors import InteractorStrict
from app.common.b_application.enums import ResponseStatusEnum
from app.common.b_application.exceptions import GatewayError
from app.distinct.user.a_domain.exceptions.existence import UsernameAlreadyExists
from app.distinct.user.a_domain.vo_user import Username
from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.sign_up.b_payload import SignUpRequest, SignUpResponse

log = logging.getLogger(__name__)


class SignUpInteractor(InteractorStrict[SignUpRequest, SignUpResponse]):
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        """
        :raises GatewayError:
        :raises UsernameAlreadyExists:
        """
        username: Username = Username(request_data.username)
        password: str = request_data.password
        try:
            await self._auth_service.sign_up(username, password)
        except (GatewayError, UsernameAlreadyExists):
            raise
        return SignUpResponse(username.value, ResponseStatusEnum.CREATED)
