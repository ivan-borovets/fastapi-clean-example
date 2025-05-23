from collections.abc import Iterable

from dishka import Provider

from app.setup.ioc.di_providers.application import UserApplicationProvider
from app.setup.ioc.di_providers.domain import UserDomainProvider
from app.setup.ioc.di_providers.infrastructure import (
    AuthInfrastructureProvider,
    CommonInfrastructureProvider,
    UserInfrastructureProvider,
)
from app.setup.ioc.di_providers.settings import (
    AuthSettingsProvider,
    CommonSettingsProvider,
    UserSettingsProvider,
)


def get_providers() -> Iterable[Provider]:
    return (
        # Domain
        UserDomainProvider(),
        # Application
        UserApplicationProvider(),
        # Infrastructure
        CommonInfrastructureProvider(),
        UserInfrastructureProvider(),
        AuthInfrastructureProvider(),
        # Settings
        CommonSettingsProvider(),
        UserSettingsProvider(),
        AuthSettingsProvider(),
    )
