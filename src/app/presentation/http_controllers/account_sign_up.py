from typing import Annotated

from dishka import FromComponent
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, status

from app.infrastructure.auth_context.sign_up import (
    SignUpHandler,
    SignUpRequest,
    SignUpResponse,
)
from app.presentation.common.exception_handler import (
    ExceptionSchema,
    ExceptionSchemaRich,
)
from app.setup.ioc.di_component_enum import ComponentEnum

sign_up_router = APIRouter()


@sign_up_router.post(
    "/signup",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ExceptionSchema},
        status.HTTP_401_UNAUTHORIZED: {"model": ExceptionSchema},
        status.HTTP_409_CONFLICT: {"model": ExceptionSchema},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ExceptionSchemaRich},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ExceptionSchema},
    },
    status_code=status.HTTP_201_CREATED,
)
@inject
async def sign_up(
    request_data: SignUpRequest,
    interactor: Annotated[
        SignUpHandler,
        FromComponent(ComponentEnum.AUTH),
    ],
) -> SignUpResponse:
    # :raises AlreadyAuthenticatedError 401:
    # :raises DomainFieldError 400:
    # :raises DataMapperError 500:
    # :raises UsernameAlreadyExists 409:
    return await interactor(request_data)
