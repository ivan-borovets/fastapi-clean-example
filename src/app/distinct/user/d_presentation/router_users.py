from fastapi import APIRouter

from app.distinct.user.scenarios.create_user.d_handler import create_user_router
from app.distinct.user.scenarios.grant_admin.d_handler import grant_admin_router
from app.distinct.user.scenarios.inactivate_user.d_handler import inactivate_user_router
from app.distinct.user.scenarios.list_users.d_handler import list_users_router
from app.distinct.user.scenarios.reactivate_user.d_handler import reactivate_user_router
from app.distinct.user.scenarios.revoke_admin.d_handler import revoke_admin_router

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
