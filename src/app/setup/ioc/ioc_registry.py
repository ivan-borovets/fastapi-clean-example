from typing import Iterable

from dishka import Provider

from app.setup.ioc.di_providers.common.connection import CommonConnectionInfraProvider
from app.setup.ioc.di_providers.common.settings import (
    CommonSettingsProvider,
    SettingsFromContextProvider,
)
from app.setup.ioc.di_providers.session_context.connection import (
    SessionConnectionInfraProvider,
)
from app.setup.ioc.di_providers.session_context.infrastructure import (
    SessionInfraConcreteProvider,
    SessionInfraDataMappersProvider,
    SessionInfraInteractorProvider,
    SessionInfraPortsProvider,
)
from app.setup.ioc.di_providers.session_context.settings import SessionSettingsProvider
from app.setup.ioc.di_providers.user.application import (
    UserApplicationDataGatewaysProvider,
    UserApplicationInteractorsProvider,
    UserApplicationPortsProvider,
    UserApplicationServicesProvider,
)
from app.setup.ioc.di_providers.user.connection import UserConnectionInfraProvider
from app.setup.ioc.di_providers.user.domain import (
    UserDomainPortsProvider,
    UserDomainServicesProvider,
)
from app.setup.ioc.di_providers.user.settings import UserSettingsProvider


def get_providers() -> Iterable[Provider]:
    settings = (
        SettingsFromContextProvider(),
        CommonSettingsProvider(),
        UserSettingsProvider(),
        SessionSettingsProvider(),
    )

    connection_common = (CommonConnectionInfraProvider(),)
    connection_user = (UserConnectionInfraProvider(),)
    connection_session = (SessionConnectionInfraProvider(),)

    domain_user = (
        UserDomainServicesProvider(),
        UserDomainPortsProvider(),
    )

    application_user = (
        UserApplicationServicesProvider(),
        UserApplicationDataGatewaysProvider(),
        UserApplicationPortsProvider(),
        UserApplicationInteractorsProvider(),
    )

    infrastructure_session = (
        SessionInfraDataMappersProvider(),
        SessionInfraPortsProvider(),
        SessionInfraConcreteProvider(),
        SessionInfraInteractorProvider(),
    )

    return (
        *settings,
        *connection_common,
        *connection_user,
        *connection_session,
        *domain_user,
        *application_user,
        *infrastructure_session,
    )
