# pylint: disable=C0301 (line-too-long)

from dishka import AnyOf, Provider, Scope, provide

from app.application.user.protocols.account_user_service import AccountUserService
from app.application.user.protocols.admin_user_service import AdminUserService
from app.application.user.services.account import AccountService
from app.application.user.services.authentication import AuthenticationService
from app.application.user.services.authorization import AuthorizationService
from app.application.user.services.session import SessionService
from app.application.user.services.token import TokenService
from app.application.user.services.user import UserService
from app.scenarios.user.create_user.application_interactor import CreateUserInteractor
from app.scenarios.user.grant_admin.application_interactor import GrantAdminInteractor
from app.scenarios.user.inactivate_user.application_interactor import (
    InactivateUserInteractor,
)
from app.scenarios.user.list_users.application_interactor import ListUsersInteractor
from app.scenarios.user.reactivate_user.application_interactor import (
    ReactivateUserInteractor,
)
from app.scenarios.user.revoke_admin.application_interactor import RevokeAdminInteractor


class UserApplicationProvider(Provider):
    account_service = provide(
        source=AccountService,
        scope=Scope.REQUEST,
    )
    user_service = provide(
        source=UserService,
        scope=Scope.REQUEST,
        provides=AnyOf[AccountUserService, AdminUserService],
    )
    authentication_service = provide(
        source=AuthenticationService,
        scope=Scope.REQUEST,
    )
    session_service = provide(
        source=SessionService,
        scope=Scope.REQUEST,
    )
    token_service = provide(
        source=TokenService,
        scope=Scope.REQUEST,
    )
    authorization_service = provide(
        source=AuthorizationService,
        scope=Scope.REQUEST,
    )

    create_user = provide(
        source=CreateUserInteractor,
        scope=Scope.REQUEST,
    )
    list_users = provide(
        source=ListUsersInteractor,
        scope=Scope.REQUEST,
    )
    inactivate_user = provide(
        source=InactivateUserInteractor,
        scope=Scope.REQUEST,
    )
    reactivate_user = provide(
        source=ReactivateUserInteractor,
        scope=Scope.REQUEST,
    )
    grant_admin = provide(
        source=GrantAdminInteractor,
        scope=Scope.REQUEST,
    )
    revoke_admin = provide(
        source=RevokeAdminInteractor,
        scope=Scope.REQUEST,
    )
