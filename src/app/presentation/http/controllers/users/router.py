from fastapi import APIRouter

from app.presentation.http.controllers.users.activate_user import (
    create_activate_user_router,
)
from app.presentation.http.controllers.users.change_password import (
    create_change_password_router,
)
from app.presentation.http.controllers.users.create_user import (
    create_create_user_router,
)
from app.presentation.http.controllers.users.deactivate_user import (
    create_deactivate_user_router,
)
from app.presentation.http.controllers.users.grant_admin import (
    create_grant_admin_router,
)
from app.presentation.http.controllers.users.list_users import create_list_users_router
from app.presentation.http.controllers.users.revoke_admin import (
    create_revoke_admin_router,
)


def create_users_router() -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["Users"],
    )

    sub_routers = (
        create_create_user_router(),
        create_list_users_router(),
        create_change_password_router(),
        create_grant_admin_router(),
        create_revoke_admin_router(),
        create_activate_user_router(),
        create_deactivate_user_router(),
    )

    for sub_router in sub_routers:
        router.include_router(sub_router)

    return router
