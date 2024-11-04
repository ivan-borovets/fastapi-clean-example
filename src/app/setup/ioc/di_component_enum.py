from enum import StrEnum


class ComponentEnum(StrEnum):
    DEFAULT = ""
    USER = "user"
    AUTH = "auth"

    def __repr__(self):
        return self.value
