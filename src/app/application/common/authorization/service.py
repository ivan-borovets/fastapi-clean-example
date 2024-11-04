import logging

from app.application.common.authorization.config import PermissionEnum
from app.application.common.authorization.role_permission_resolver import (
    RolePermissionResolver,
)
from app.application.common.exceptions.authorization import AuthorizationError
from app.application.common.ports.command_gateways.user import UserCommandGateway
from app.application.common.ports.identity_provider import IdentityProvider
from app.domain.entities.user.entity import User
from app.domain.entities.user.role_enum import UserRoleEnum
from app.domain.entities.user.value_objects import UserId

log = logging.getLogger(__name__)


class AuthorizationService:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_command_gateway: UserCommandGateway,
        role_permission_resolver: RolePermissionResolver,
    ):
        self._identity_provider = identity_provider
        self._user_command_gateway = user_command_gateway
        self._role_permission_resolver = role_permission_resolver
        self._current_user: User | None = None
        self._current_user_transitive_roles: set[UserRoleEnum] | None = None

    async def _get_current_user(self) -> User:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        if self._current_user is None:
            current_user_id: UserId = (
                await self._identity_provider.get_current_user_id()
            )
            current_user: User | None = await self._user_command_gateway.read_by_id(
                current_user_id
            )
            if current_user is None:
                log.debug("Failed to retrieve current user.")
                raise AuthorizationError("Not authorized.")
            self._current_user = current_user
        return self._current_user

    def _get_transitive_roles(self, role: UserRoleEnum) -> set[UserRoleEnum]:
        if self._current_user_transitive_roles is None:
            self._current_user_transitive_roles = (
                self._role_permission_resolver.compute_transitive_roles(role)
            )
        return self._current_user_transitive_roles

    def _get_transitive_permissions(
        self, transitive_roles: set[UserRoleEnum]
    ) -> set[PermissionEnum]:
        transitive_permissions: set[PermissionEnum] = (
            self._role_permission_resolver.compute_transitive_permissions(
                transitive_roles
            )
        )
        return transitive_permissions

    async def authorize_action(
        self,
        permission_required: PermissionEnum,
    ) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        current_user: User = await self._get_current_user()

        if current_user.role == UserRoleEnum.SUPER_ADMIN:
            return

        transitive_roles: set[UserRoleEnum] = self._get_transitive_roles(
            current_user.role
        )
        transitive_permissions: set[PermissionEnum] = self._get_transitive_permissions(
            transitive_roles
        )

        if (
            PermissionEnum.ALL not in transitive_permissions
            and permission_required not in transitive_permissions
        ):
            log.debug(
                "User '%s' lacks permission '%s'.",
                current_user.id_,
                permission_required,
            )
            raise AuthorizationError("Not authorized.")

    async def authorize_action_by_role(
        self,
        target_role: UserRoleEnum,
        for_subordinate_only: bool = False,
    ) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        current_user = await self._get_current_user()

        if current_user.role == UserRoleEnum.SUPER_ADMIN:
            return

        transitive_roles = self._get_transitive_roles(current_user.role)

        if for_subordinate_only:
            transitive_roles.discard(current_user.role)

        if target_role not in transitive_roles:
            raise AuthorizationError("Not authorized.")

    async def authorize_action_by_user(
        self,
        target_user: User,
        for_subordinate_only: bool = False,
    ) -> None:
        """
        :raises AuthenticationError:
        :raises DataMapperError:
        :raises AuthorizationError:
        """
        current_user = await self._get_current_user()

        if current_user.role == UserRoleEnum.SUPER_ADMIN:
            return

        if current_user.id_ == target_user.id_:
            await self.authorize_action(PermissionEnum.EDIT_SELF)
            return

        await self.authorize_action(PermissionEnum.MANAGE_USERS)

        transitive_roles = self._get_transitive_roles(current_user.role)
        if for_subordinate_only:
            transitive_roles.discard(current_user.role)

        if target_user.role not in transitive_roles:
            log.debug(
                "User '%s' cannot interact with user '%s' due to role restrictions.",
                current_user.id_,
                target_user.id_,
            )
            raise AuthorizationError("Not authorized.")
