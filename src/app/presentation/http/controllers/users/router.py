from fastapi import APIRouter

from app.presentation.http.controllers.users.activate_user import (
    activate_user_router,
)
from app.presentation.http.controllers.users.change_password import (
    change_password_router,
)
from app.presentation.http.controllers.users.create_user import (
    create_user_router,
)
from app.presentation.http.controllers.users.deactivate_user import (
    deactivate_user_router,
)
from app.presentation.http.controllers.users.grant_admin import grant_admin_router
from app.presentation.http.controllers.users.list_users import (
    list_users_router,
)
from app.presentation.http.controllers.users.revoke_admin import (
    revoke_admin_router,
)

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
users_sub_routers: tuple[APIRouter, ...] = (
    create_user_router,
    list_users_router,
    change_password_router,
    grant_admin_router,
    revoke_admin_router,
    activate_user_router,
    deactivate_user_router,
)

for router in users_sub_routers:
    users_router.include_router(router)
