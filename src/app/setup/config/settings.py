import logging
import os
from datetime import timedelta
from typing import Any, Literal, Self

import rtoml
from pydantic import BaseModel, Field, PostgresDsn, field_validator

from app.setup.config.constants import (
    ENV_TO_DIR_PATHS,
    ENV_VAR_NAME,
    DirContents,
    ValidEnvs,
)

log = logging.getLogger(__name__)


class PasswordSettings(BaseModel):
    pepper: str = Field(alias="PEPPER")


class AuthSettings(BaseModel):
    jwt_secret: str = Field(alias="JWT_SECRET")
    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ] = Field(alias="JWT_ALGORITHM")
    session_ttl_min: timedelta = Field(alias="SESSION_TTL_MIN")
    session_refresh_threshold: float = Field(alias="SESSION_REFRESH_THRESHOLD")

    @field_validator("session_ttl_min", mode="before")
    @classmethod
    def convert_session_ttl_min(cls, v: Any) -> timedelta:
        if isinstance(v, (int, float)):
            if v < 1:
                raise ValueError("SESSION_TTL_MIN must be at least 1 (n of minutes).")
            return timedelta(minutes=v)
        else:
            raise ValueError("SESSION_TTL_MIN must be a number (n of minutes, n >= 1).")

    @field_validator("session_refresh_threshold", mode="before")
    @classmethod
    def validate_session_refresh_threshold(cls, v: Any) -> float:
        if isinstance(v, (int, float)):
            if not 0 < v < 1:
                raise ValueError(
                    "SESSION_REFRESH_THRESHOLD must be between 0 and 1, exclusive."
                )
            return v
        else:
            raise ValueError(
                "SESSION_REFRESH_THRESHOLD must be a number "
                "(fraction, 0 < fraction < 1)."
            )


class CookiesSettings(BaseModel):
    secure: bool = Field(alias="SECURE")


class SecuritySettings(BaseModel):
    password: PasswordSettings
    auth: AuthSettings
    cookies: CookiesSettings


class PostgresSettings(BaseModel):
    user: str = Field(alias="USER")
    password: str = Field(alias="PASSWORD")
    db: str = Field(alias="DB")
    host: str = Field(alias="HOST")
    port: int = Field(alias="PORT")
    driver: str = Field(alias="DRIVER")

    @field_validator("host")
    @classmethod
    def override_host_from_env(cls, v: str) -> str:
        postgres_host_env = os.environ.get("POSTGRES_HOST")
        if postgres_host_env:
            return postgres_host_env
        return v

    @field_validator("port")
    @classmethod
    def validate_port_range(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{self.driver}",
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.db,
            )
        )


class SqlaEngineSettings(BaseModel):
    echo: bool = Field(alias="ECHO")
    echo_pool: bool = Field(alias="ECHO_POOL")
    pool_size: int = Field(alias="POOL_SIZE")
    max_overflow: int = Field(alias="MAX_OVERFLOW")


class LoggingSettings(BaseModel):
    level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = Field(alias="LEVEL")


class AppSettings(BaseModel):
    postgres: PostgresSettings
    sqla: SqlaEngineSettings
    security: SecuritySettings
    logs: LoggingSettings

    @classmethod
    def from_toml(cls, env: ValidEnvs | None = None) -> Self:
        if env is None:
            env = get_current_env()
        raw_config = load_full_config(env=env)
        log.info("Reading config for environment: '%s'", env)
        return cls.model_validate(raw_config)


def validate_env(*, env: str | None) -> ValidEnvs:
    if env is None or env not in ValidEnvs:
        valid_values = ", ".join(f"'{e}'" for e in ValidEnvs)
        env_display = "not set" if env is None else f"'{env}'"
        raise ValueError(
            f"Environment variable {ENV_VAR_NAME} has invalid value: {env_display}. "
            f"Must be one of: {valid_values}."
        )
    return ValidEnvs(env)


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
            f"The file does not exist at the specified path: {file_path}"
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


def get_current_env() -> ValidEnvs:
    env_value = os.environ.get(ENV_VAR_NAME)
    return validate_env(env=env_value)


def load_settings(env: ValidEnvs | None = None) -> AppSettings:
    return AppSettings.from_toml(env=env)
