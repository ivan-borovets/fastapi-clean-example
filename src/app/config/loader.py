from pathlib import Path
from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.settings import (
    AppSettings,
    CookieSettings,
    JwtSettings,
    PasswordHasherSettings,
    PostgresSettings,
    SessionSettings,
    SqlaSettings,
)

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[3]
_ENV_FILE: Final[Path] = BASE_DIR.joinpath(".env")
_DEFAULT_CONFIG_DICT: Final[SettingsConfigDict] = SettingsConfigDict(
    env_file=_ENV_FILE,
    env_file_encoding="utf-8",
    extra="ignore",
)


def _load_settings[E: BaseSettings](env_cls: type[E]) -> E:
    return env_cls()


class AppEnvConfig(BaseSettings, AppSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="APP_")


class PostgresEnvConfig(BaseSettings, PostgresSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="POSTGRES_")


class SqlaEnvConfig(BaseSettings, SqlaSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="SQLA_")


class PasswordHasherEnvConfig(BaseSettings, PasswordHasherSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="PASSWORD_")


class JwtEnvConfig(BaseSettings, JwtSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="JWT_")


class SessionEnvConfig(BaseSettings, SessionSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="SESSION_")


class CookieEnvConfig(BaseSettings, CookieSettings):
    model_config = _DEFAULT_CONFIG_DICT | SettingsConfigDict(env_prefix="COOKIE_")


def load_app_settings() -> AppSettings:
    return _load_settings(AppEnvConfig)


def load_postgres_settings() -> PostgresSettings:
    return _load_settings(PostgresEnvConfig)


def load_sqla_settings() -> SqlaSettings:
    return _load_settings(SqlaEnvConfig)


def load_password_hasher_settings() -> PasswordHasherSettings:
    return _load_settings(PasswordHasherEnvConfig)


def load_jwt_settings() -> JwtSettings:
    return _load_settings(JwtEnvConfig)


def load_session_settings() -> SessionSettings:
    return _load_settings(SessionEnvConfig)


def load_cookie_settings() -> CookieSettings:
    return _load_settings(CookieEnvConfig)
