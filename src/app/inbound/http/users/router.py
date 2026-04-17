from fastapi import APIRouter, Depends
from fastapi.security import APIKeyCookie

from app.inbound.http.users.activate_user import make_activate_user_router
from app.inbound.http.users.create_user import make_create_user_router
from app.inbound.http.users.deactivate_user import make_deactivate_user_router
from app.inbound.http.users.grant_admin import make_grant_admin_router
from app.inbound.http.users.list_users import make_list_users_router
from app.inbound.http.users.revoke_admin import make_revoke_admin_router
from app.inbound.http.users.set_user_password import make_set_user_password_router


def make_users_router(*, cookie_name: str) -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["Users"],
        dependencies=[Depends(APIKeyCookie(name=cookie_name))],
    )
    router.include_router(make_create_user_router())
    router.include_router(make_list_users_router())
    router.include_router(make_set_user_password_router())
    router.include_router(make_grant_admin_router())
    router.include_router(make_revoke_admin_router())
    router.include_router(make_activate_user_router())
    router.include_router(make_deactivate_user_router())
    return router
