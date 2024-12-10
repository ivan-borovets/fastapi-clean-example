from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.infrastructure.session.scenarios.sign_up.interactor import SignUpInteractor
from app.infrastructure.session.scenarios.sign_up.payload import (
    SignUpRequest,
    SignUpResponse,
)
from app.presentation.exception_handler import ExceptionSchema
from app.setup.ioc.enum_component import ComponentEnum

sign_up_router = APIRouter()


@sign_up_router.post(
    "/signup",
    responses={
        status.HTTP_201_CREATED: {"model": SignUpResponse},
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
)
@inject
async def sign_up(
    request_data: SignUpRequest,
    interactor: Annotated[
        SignUpInteractor,
        FromComponent(ComponentEnum.SESSION),
    ],
) -> SignUpResponse:
    # :raises AlreadyAuthenticatedError 401:
    # :raises DomainFieldError 400:
    # :raises DataMapperError 500:
    # :raises UsernameAlreadyExists 409:
    return await interactor(request_data)
