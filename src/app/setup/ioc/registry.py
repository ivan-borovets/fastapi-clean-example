from typing import Iterable

from dishka import Provider

from app.setup.ioc.di_providers.auth_infrastructure import AuthInfrastructureProvider
from app.setup.ioc.di_providers.auth_settings import AuthSettingsProvider
from app.setup.ioc.di_providers.common_infrastructure import (
    CommonInfrastructureProvider,
)
from app.setup.ioc.di_providers.common_settings import CommonSettingsProvider
from app.setup.ioc.di_providers.user_application import UserApplicationProvider
from app.setup.ioc.di_providers.user_domain import UserDomainProvider
from app.setup.ioc.di_providers.user_infrastructure import UserInfrastructureProvider
from app.setup.ioc.di_providers.user_settings import UserSettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        AuthInfrastructureProvider(),
        AuthSettingsProvider(),
        CommonInfrastructureProvider(),
        CommonSettingsProvider(),
        UserApplicationProvider(),
        UserDomainProvider(),
        UserInfrastructureProvider(),
        UserSettingsProvider(),
    )
