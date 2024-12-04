from enum import StrEnum


class ComponentEnum(StrEnum):
    DEFAULT = ""
    USER = "user"
    SESSION = "session"

    def __repr__(self):
        return self.value
