from fastapi import APIRouter

from app.inbound.http.account.router import make_account_router
from app.inbound.http.users.router import make_users_router


def make_v1_router(*, cookie_name: str) -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    router.include_router(make_account_router(cookie_name=cookie_name))
    router.include_router(make_users_router(cookie_name=cookie_name))
    return router
