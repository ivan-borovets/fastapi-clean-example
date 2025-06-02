from fastapi import APIRouter

from app.presentation.web.controllers.users.change_password import (
    change_password_router,
)
from app.presentation.web.controllers.users.create_user import (
    create_user_router,
)
from app.presentation.web.controllers.users.grant_admin import grant_admin_router
from app.presentation.web.controllers.users.inactivate_user import (
    inactivate_user_router,
)
from app.presentation.web.controllers.users.list_users import (
    list_users_router,
)
from app.presentation.web.controllers.users.reactivate_user import (
    reactivate_user_router,
)
from app.presentation.web.controllers.users.revoke_admin import (
    revoke_admin_router,
)

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)
users_sub_routers: tuple[APIRouter, ...] = (
    change_password_router,
    create_user_router,
    grant_admin_router,
    inactivate_user_router,
    list_users_router,
    reactivate_user_router,
    revoke_admin_router,
)

for router in users_sub_routers:
    users_router.include_router(router)
