from collections.abc import Iterable

from dishka import Provider

from app.setup.ioc.di_providers.application import ApplicationProvider
from app.setup.ioc.di_providers.domain import DomainProvider
from app.setup.ioc.di_providers.infrastructure import infrastructure_provider
from app.setup.ioc.di_providers.presentation import PresentationProvider
from app.setup.ioc.di_providers.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        DomainProvider(),
        ApplicationProvider(),
        infrastructure_provider(),
        PresentationProvider(),
        SettingsProvider(),
    )
