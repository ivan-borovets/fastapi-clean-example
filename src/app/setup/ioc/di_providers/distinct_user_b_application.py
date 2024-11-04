# pylint: disable=C0301 (line-too-long)

from dishka import Provider, Scope, provide

from app.distinct.user.b_application.service_auth import AuthService
from app.distinct.user.scenarios.create_user.b_interactor import CreateUserInteractor
from app.distinct.user.scenarios.grant_admin.b_interactor import GrantAdminInteractor
from app.distinct.user.scenarios.inactivate_user.b_interactor import (
    InactivateUserInteractor,
)
from app.distinct.user.scenarios.list_users.b_interactor import ListUsersInteractor
from app.distinct.user.scenarios.log_in.b_interactor import LogInInteractor
from app.distinct.user.scenarios.log_out.b_interactor import LogOutInteractor
from app.distinct.user.scenarios.reactivate_user.b_interactor import (
    ReactivateUserInteractor,
)
from app.distinct.user.scenarios.revoke_admin.b_interactor import RevokeAdminInteractor
from app.distinct.user.scenarios.sign_up.b_interactor import SignUpInteractor


class UserApplicationProvider(Provider):
    auth_service = provide(
        source=AuthService,
        scope=Scope.REQUEST,
    )
    sign_up = provide(
        source=SignUpInteractor,
        scope=Scope.REQUEST,
    )
    log_in = provide(
        source=LogInInteractor,
        scope=Scope.REQUEST,
    )
    log_out = provide(
        source=LogOutInteractor,
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
