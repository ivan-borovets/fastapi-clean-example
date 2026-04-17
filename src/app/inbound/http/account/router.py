from fastapi import APIRouter

from app.inbound.http.account.change_password import make_change_password_router
from app.inbound.http.account.log_in import make_log_in_router
from app.inbound.http.account.log_out import make_log_out_router
from app.inbound.http.account.sign_up import make_sign_up_router


def make_account_router(*, cookie_name: str) -> APIRouter:
    router = APIRouter(prefix="/account", tags=["Account"])
    router.include_router(make_sign_up_router())
    router.include_router(make_log_in_router())
    router.include_router(make_change_password_router(cookie_name=cookie_name))
    router.include_router(make_log_out_router(cookie_name=cookie_name))
    return router
