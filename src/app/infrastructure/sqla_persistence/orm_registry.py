from types import MappingProxyType
from typing import Final

from sqlalchemy import MetaData
from sqlalchemy.orm import registry

NAMING_CONVENTIONS: Final[MappingProxyType[str, str]] = MappingProxyType({
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})

mapping_registry = registry(metadata=MetaData(naming_convention=NAMING_CONVENTIONS))
