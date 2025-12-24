from collections.abc import Iterable

from dishka import Provider

from app.setup.ioc.application import ApplicationProvider
from app.setup.ioc.domain import DomainProvider
from app.setup.ioc.infrastructure import infrastructure_providers
from app.setup.ioc.presentation import PresentationProvider
from app.setup.ioc.settings import SettingsProvider


def get_providers() -> Iterable[Provider]:
    return (
        DomainProvider(),
        ApplicationProvider(),
        *infrastructure_providers(),
        PresentationProvider(),
        SettingsProvider(),
    )
