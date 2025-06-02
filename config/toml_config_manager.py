import logging
import os
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

import rtoml

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
    except ValueError as e:
        raise ValueError(f"Invalid log level: '{level}'.") from e


def configure_logging(*, level: LoggingLevel = DEFAULT_LOG_LEVEL) -> None:
    logging.getLogger().handlers.clear()

    level_map: dict[LoggingLevel, int] = {
        LoggingLevel.DEBUG: logging.DEBUG,
        LoggingLevel.INFO: logging.INFO,
        LoggingLevel.WARNING: logging.WARNING,
        LoggingLevel.ERROR: logging.ERROR,
        LoggingLevel.CRITICAL: logging.CRITICAL,
    }

    logging.basicConfig(
        level=level_map[level],
        datefmt="%Y-%m-%d %H:%M:%S",
        format=(
            "[%(asctime)s.%(msecs)03d] "
            "%(funcName)20s "
            "%(module)s:%(lineno)d "
            "%(levelname)-8s - "
            "%(message)s"
        ),
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


BASE_DIR_PATH: Final[Path] = Path(__file__).resolve().parent.parent
CONFIG_PATH: Final[Path] = BASE_DIR_PATH / "config"


ENV_TO_DIR_PATHS: Final[MappingProxyType[ValidEnvs, Path]] = MappingProxyType({
    ValidEnvs.LOCAL: CONFIG_PATH / ValidEnvs.LOCAL,
    ValidEnvs.DEV: CONFIG_PATH / ValidEnvs.DEV,
    ValidEnvs.PROD: CONFIG_PATH / ValidEnvs.PROD,
})


def validate_env(*, env: str | None) -> ValidEnvs:
    if env is None:
        raise ValueError(f"{ENV_VAR_NAME} is not set.")
    try:
        return ValidEnvs(env)
    except ValueError as e:
        valid_values = ", ".join(f"'{e}'" for e in ValidEnvs)
        raise ValueError(
            f"Invalid {ENV_VAR_NAME}: '{env}'. Must be one of: {valid_values}.",
        ) from e


def get_current_env() -> ValidEnvs:
    env_value = os.getenv(ENV_VAR_NAME)
    return validate_env(env=env_value)


# CONFIG READING


def read_config(
    *,
    env: ValidEnvs,
    config: DirContents = DirContents.CONFIG_NAME,
) -> dict[str, Any]:
    dir_path = ENV_TO_DIR_PATHS.get(env)
    if dir_path is None:
        raise FileNotFoundError(f"No directory path configured for environment: {env}")
    file_path = dir_path / config
    if not file_path.is_file():
        raise FileNotFoundError(
            f"The file does not exist at the specified path: {file_path}",
        )
    with open(file=file_path, mode="r", encoding="utf-8") as file:
        return rtoml.load(file)


def merge_dicts(*, dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(dict1=result[key], dict2=value)
        else:
            result[key] = value
    return result


def load_full_config(*, env: ValidEnvs) -> dict[str, Any]:
    config = read_config(env=env)
    try:
        secrets = read_config(env=env, config=DirContents.SECRETS_NAME)
    except FileNotFoundError:
        log.warning("Secrets file not found. Full config will not contain secrets.")
    else:
        config = merge_dicts(dict1=config, dict2=secrets)
    return config


# EXPORT PROCESSING


def get_env_value_by_export_field(*, config: dict[str, Any], field: str) -> Any:
    parts = field.split(".")
    current = config
    for part in parts:
        if part not in current:
            raise KeyError(f"Field '{field}' not found in config")
        current = current[part]

    if isinstance(current, (dict, list)):
        raise ValueError(
            f"Field '{field}' cannot be converted to string: "
            f"got {type(current).__name__}",
        )
    try:
        return str(current)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Field '{field}' cannot be converted to string: {e!s}") from e


def extract_exported(
    *,
    config: dict[str, Any],
    export_fields: list[str],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for field in export_fields:
        str_value = get_env_value_by_export_field(config=config, field=field)
        env_key = "_".join(part.upper() for part in field.split("."))
        result[env_key] = str_value
    return result


def load_export_fields(*, env: ValidEnvs) -> tuple[dict[str, Any], list[str]]:
    config = load_full_config(env=env)
    export_data = read_config(env=env, config=DirContents.EXPORT_NAME)
    if "export" not in export_data or "fields" not in export_data["export"]:
        raise ValueError("Invalid export.toml: missing [export] section or 'fields'")
    export_fields = export_data["export"]["fields"]
    return config, export_fields


# DOTENV GENERATION


def write_dotenv_file(*, env: ValidEnvs, exported_fields: dict[str, str]) -> None:
    env_filename = f"{DirContents.DOTENV_NAME}.{env.value}"
    env_path = ENV_TO_DIR_PATHS[env] / env_filename
    header = [
        "# This .env file was automatically generated by toml_config_manager.",
        "# Do not edit directly. Make changes in config.toml or .secrets.toml instead.",
        "# Ensure values here match those in config files.",
        f"# Environment: {env}",
        f"# Generated: {datetime.now(UTC).isoformat()}",
    ]
    body = [f"{key}={value}" for key, value in exported_fields.items()]
    body.append("")

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header + body))

    try:
        relative_path = env_path.relative_to(BASE_DIR_PATH)
    except ValueError:
        relative_path = env_path

    log.info(
        "Dotenv for environment '%s' was successfully generated at '%s'! ✨",
        env.value,
        relative_path,
    )


def generate_dotenv(*, env: ValidEnvs) -> None:
    config, export_fields = load_export_fields(env=env)
    exported_fields = extract_exported(config=config, export_fields=export_fields)
    write_dotenv_file(env=env, exported_fields=exported_fields)


# ENTRY POINT


def main() -> None:
    log_lvl: str = os.getenv(LOG_LEVEL_VAR_NAME, DEFAULT_LOG_LEVEL)
    validated_log_lvl: LoggingLevel = validate_logging_level(level=log_lvl)
    configure_logging(level=validated_log_lvl)

    current_env = get_current_env()
    generate_dotenv(env=current_env)


if __name__ == "__main__":
    main()
