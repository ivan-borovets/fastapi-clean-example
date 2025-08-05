from fastapi import APIRouter

from app.presentation.http.controllers.account.log_in import create_log_in_router
from app.presentation.http.controllers.account.log_out import (
    create_log_out_router,
)
from app.presentation.http.controllers.account.sign_up import (
    create_sign_up_router,
)


def create_account_router() -> APIRouter:
    router = APIRouter(
        prefix="/account",
        tags=["Account"],
    )

    sub_routers = (
        create_sign_up_router(),
        create_log_in_router(),
        create_log_out_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
