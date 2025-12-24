from fastapi import APIRouter

from app.presentation.http.controllers.account.change_password import (
    create_change_password_router,
)
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
    router.include_router(create_sign_up_router())
    router.include_router(create_log_in_router())
    router.include_router(create_change_password_router())
    router.include_router(create_log_out_router())
    return router
