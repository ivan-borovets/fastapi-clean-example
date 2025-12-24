from fastapi import APIRouter

from app.presentation.http.controllers.users.activate_user import (
    create_activate_user_router,
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
from app.presentation.http.controllers.users.set_user_password import (
    create_set_user_password_router,
)


def create_users_router() -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["Users"],
    )
    router.include_router(create_create_user_router())
    router.include_router(create_list_users_router())
    router.include_router(create_set_user_password_router())
    router.include_router(create_grant_admin_router())
    router.include_router(create_revoke_admin_router())
    router.include_router(create_activate_user_router())
    router.include_router(create_deactivate_user_router())
    return router
