from typing import Iterable

from dishka import Provider

from app.setup.ioc.di_providers.common_c_infrastructure import (
    CommonInfrastructureProvider,
)
from app.setup.ioc.di_providers.distinct_user_b_application import (
    UserApplicationProvider,
)
from app.setup.ioc.di_providers.distinct_user_c_infrastructure import (
    UserAdaptersProvider,
    UserGatewaysProvider,
)
from app.setup.ioc.di_providers.distinct_user_d_presentation import (
    UserPresentationProvider,
)
from app.setup.ioc.di_providers.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    common_c_infrastructure = (CommonInfrastructureProvider(),)
    distinct_user_b_application = (UserApplicationProvider(),)
    distinct_user_c_infrastructure = (
        UserGatewaysProvider(),
        UserAdaptersProvider(),
    )
    distinct_user_d_presentation = (UserPresentationProvider(),)
    settings = (SettingsProvider(),)

    return (
        *common_c_infrastructure,
        *distinct_user_b_application,
        *distinct_user_c_infrastructure,
        *distinct_user_d_presentation,
        *settings,
    )
