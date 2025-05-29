from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Final

ENV_VAR_NAME: Final[str] = "APP_ENV"


class ValidEnvs(StrEnum):
    """
    Values should reflect actual directory names.
    """

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class DirContents(StrEnum):
    """
    Values should reflect actual file names.
    """

    CONFIG_NAME = "config.toml"
    SECRETS_NAME = ".secrets.toml"
    EXPORT_NAME = "export.toml"
    DOTENV_NAME = ".env"


BASE_DIR_PATH: Final[Path] = Path(__file__).resolve().parent.parent.parent.parent.parent
CONFIG_PATH: Final[Path] = BASE_DIR_PATH / "config"


ENV_TO_DIR_PATHS: Final[MappingProxyType[ValidEnvs, Path]] = MappingProxyType({
    ValidEnvs.LOCAL: CONFIG_PATH / ValidEnvs.LOCAL,
    ValidEnvs.DEV: CONFIG_PATH / ValidEnvs.DEV,
    ValidEnvs.PROD: CONFIG_PATH / ValidEnvs.PROD,
})
