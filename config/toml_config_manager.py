import logging
import os
import tomllib
from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

ConfigDict = dict[str, Any]
ExportEnv = dict[str, str]

log = logging.getLogger(__name__)


# LOGGING


LOG_LEVEL_VAR_NAME: Final[str] = "LOG_LEVEL"


class LoggingLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


DEFAULT_LOG_LEVEL: Final[LoggingLevel] = LoggingLevel.INFO


def validate_logging_level(*, level: str) -> LoggingLevel:
    try:
        return LoggingLevel(level)
    except ValueError as err:
        raise ValueError(f"Invalid log level: '{level}'.") from err


FMT: Final[str] = (
    "[%(asctime)s.%(msecs)03d] "
    "[%(threadName)s] "
    "%(funcName)20s "
    "%(module)s:%(lineno)d "
    "%(levelname)-8s - "
    "%(message)s"
)
DATEFMT: Final[str] = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    *,
    level: LoggingLevel = DEFAULT_LOG_LEVEL,
) -> None:
    logging.basicConfig(
        level=level,
        datefmt=DATEFMT,
        format=FMT,
        force=True,
    )


# ENVIRONMENT & PATHS


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


BASE_DIR_PATH: Final[Path] = Path(__file__).resolve().parents[1]
CONFIG_PATH: Final[Path] = BASE_DIR_PATH / "config"

ENV_TO_DIR_PATHS: Final[Mapping[ValidEnvs, Path]] = MappingProxyType({
    ValidEnvs.LOCAL: CONFIG_PATH / ValidEnvs.LOCAL,
    ValidEnvs.DEV: CONFIG_PATH / ValidEnvs.DEV,
    ValidEnvs.PROD: CONFIG_PATH / ValidEnvs.PROD,
})


def validate_env(env: str | None) -> ValidEnvs:
    if env is None:
        raise ValueError(f"{ENV_VAR_NAME} is not set.")
    try:
        return ValidEnvs(env)
    except ValueError as err:
        valid_values = ", ".join(f"'{e}'" for e in ValidEnvs)
        raise ValueError(
            f"Invalid {ENV_VAR_NAME}: '{env}'. Must be one of: {valid_values}.",
        ) from err


def get_current_env() -> ValidEnvs:
    return validate_env(os.getenv(ENV_VAR_NAME))


# CONFIG READING


def load_full_config(
    env: ValidEnvs,
    dir_paths: Mapping[ValidEnvs, Path] = ENV_TO_DIR_PATHS,
    main_config: DirContents = DirContents.CONFIG_NAME,
    secrets_config: DirContents = DirContents.SECRETS_NAME,
) -> ConfigDict:
    log.info("Reading config for environment: '%s'", env)
    config = read_config(env=env, config=main_config, dir_paths=dir_paths)
    try:
        secrets = read_config(env=env, config=secrets_config, dir_paths=dir_paths)
    except FileNotFoundError:
        log.warning("Secrets file not found. Full config will not contain secrets.")
        return config
    return merge_dicts(dict1=config, dict2=secrets)


def read_config(
    env: ValidEnvs,
    dir_paths: Mapping[ValidEnvs, Path],
    config: DirContents,
) -> ConfigDict:
    dir_path = dir_paths.get(env)
    if dir_path is None:
        raise FileNotFoundError(f"No directory path configured for environment: {env}")
    file_path = dir_path / config
    if not file_path.is_file():
        raise FileNotFoundError(
            f"The file does not exist at the specified path: {file_path}",
        )
    with file_path.open(mode="rb") as f:
        return tomllib.load(f)


def merge_dicts(*, dict1: ConfigDict, dict2: ConfigDict) -> ConfigDict:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(dict1=result[key], dict2=value)
        else:
            result[key] = value
    return result


# EXPORT PROCESSING


EXPORT_SECTION: Final[str] = "export"
EXPORT_FIELDS_KEY: Final[str] = "fields"


def get_exported_env_variables(
    env: ValidEnvs,
    dir_paths: Mapping[ValidEnvs, Path] = ENV_TO_DIR_PATHS,
) -> ExportEnv:
    config = load_full_config(env=env, dir_paths=dir_paths)
    export_fields = load_export_fields(env=env, dir_paths=dir_paths)
    return extract_export_fields_from_config(config=config, export_fields=export_fields)


def load_export_fields(
    env: ValidEnvs,
    dir_paths: Mapping[ValidEnvs, Path],
) -> list[str]:
    export_data = read_config(
        env=env,
        config=DirContents.EXPORT_NAME,
        dir_paths=dir_paths,
    )

    export_section = export_data.get(EXPORT_SECTION)
    if not isinstance(export_section, dict):
        raise ValueError(
            f"Invalid {DirContents.EXPORT_NAME}: missing [{EXPORT_SECTION}] section"
        )

    fields = export_section.get(EXPORT_FIELDS_KEY)
    if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
        raise ValueError(
            f"Invalid {DirContents.EXPORT_NAME}: "
            f"'{EXPORT_FIELDS_KEY}' must be a list of strings"
        )
    if not fields:
        raise ValueError(
            f"Invalid {DirContents.EXPORT_NAME}: '{EXPORT_FIELDS_KEY}' cannot be empty"
        )

    return fields


def extract_export_fields_from_config(
    config: ConfigDict,
    export_fields: list[str],
) -> ExportEnv:
    result: ExportEnv = {}
    for field in export_fields:
        str_value = get_env_value_by_export_field(config=config, field=field)
        env_key = "_".join(part.upper() for part in field.split("."))
        result[env_key] = str_value
    return result


def get_env_value_by_export_field(*, config: ConfigDict, field: str) -> str:
    node: Mapping[str, Any] = config
    value: Any = node

    parts = field.split(".")
    for idx, part in enumerate(parts):
        if part not in node:
            raise KeyError(f"Field '{field}' not found in config")

        value = node[part]

        if idx != len(parts) - 1:
            if not isinstance(value, Mapping):
                raise KeyError(f"Field '{field}' not found in config")
            node = value

    if isinstance(value, (dict, list)):
        raise ValueError(
            f"Field '{field}' cannot be converted to string: "
            f"got {type(value).__name__}",
        )

    return str(value)


# DOTENV GENERATION


def write_dotenv_file(
    *,
    env: ValidEnvs,
    exported_fields: ExportEnv,
    generated_at: datetime | None = None,
) -> None:
    if generated_at is None:
        generated_at = datetime.now(UTC)

    dotenv_filename = f"{DirContents.DOTENV_NAME}.{env.value}"
    dotenv_path = ENV_TO_DIR_PATHS[env] / dotenv_filename

    header = [
        "# This .env file was automatically generated by toml_config_manager.",
        "# Do not edit directly. Make changes in config.toml or .secrets.toml instead.",
        "# Ensure values here match those in config files.",
        f"# Environment: {env}",
        f"# Generated: {generated_at.isoformat()}",
    ]
    body = [f"{key}={value}" for key, value in exported_fields.items()]
    body.append("")

    dotenv_path.write_text(
        data="\n".join(header + body),
        encoding="utf-8",
        newline="\n",
    )

    log.info(
        "Dotenv for environment '%s' was successfully generated at '%s'! ✨",
        env.value,
        str(dotenv_path.resolve()),
    )


# ENTRY POINT


def main() -> None:
    log_lvl_str = os.getenv(LOG_LEVEL_VAR_NAME, DEFAULT_LOG_LEVEL)
    log_lvl = validate_logging_level(level=log_lvl_str)
    configure_logging(level=log_lvl)

    env = get_current_env()
    exported_fields = get_exported_env_variables(env)
    write_dotenv_file(env=env, exported_fields=exported_fields)


if __name__ == "__main__":
    main()
