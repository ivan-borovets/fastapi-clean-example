from fastapi import APIRouter

from app.presentation.http_controllers.admin_create_user import create_user_router
from app.presentation.http_controllers.admin_grant_admin import grant_admin_router
from app.presentation.http_controllers.admin_inactivate_user import (
    inactivate_user_router,
)
from app.presentation.http_controllers.admin_list_user.handler import list_users_router
from app.presentation.http_controllers.admin_reactivate_user import (
    reactivate_user_router,
)
from app.presentation.http_controllers.admin_revoke_admin import revoke_admin_router

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

users_sub_routers = (
    create_user_router,
    list_users_router,
    inactivate_user_router,
    reactivate_user_router,
    grant_admin_router,
    revoke_admin_router,
)

for router in users_sub_routers:
    users_router.include_router(router)
