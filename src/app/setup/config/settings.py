import logging
from datetime import timedelta
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, PostgresDsn, field_validator

from app.setup.config.constants import BASE_DIR
from app.setup.config.toml_reader import TomlConfigReader

log = logging.getLogger(__name__)


class PasswordSettings(BaseModel):
    pepper: str = Field(alias="PASSWORD_PEPPER")


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


class LoggingSettings(BaseModel):
    level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = Field(alias="LOG_LEVEL")


class PostgresSettings(BaseModel):
    username: str = Field(alias="POSTGRES_USER")
    password: str = Field(alias="POSTGRES_PASSWORD")
    host: str = Field(alias="POSTGRES_HOST")
    port: int = Field(alias="POSTGRES_PORT")
    path: str = Field(alias="POSTGRES_DB")

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.path,
            )
        )


class SqlaEngineSettings(BaseModel):
    echo: bool = Field(alias="SQLA_ECHO")
    echo_pool: bool = Field(alias="SQLA_ECHO_POOL")
    pool_size: int = Field(alias="SQLA_POOL_SIZE")
    max_overflow: int = Field(alias="SQLA_MAX_OVERFLOW")


class DbSettings(BaseModel):
    postgres: PostgresSettings
    sqla_engine: SqlaEngineSettings


class Settings(BaseModel):
    security: SecuritySettings
    logging: LoggingSettings
    db: DbSettings

    _cfg_toml_path: Path = BASE_DIR / "config.toml"

    @classmethod
    def from_file(
        cls,
        path: Path = _cfg_toml_path,
        reader: TomlConfigReader = TomlConfigReader(),
        strict: bool = False,
    ) -> Self:
        if not path.is_file():
            raise FileNotFoundError(
                f"The file does not exist at the specified path: {path}"
            )
        config_data = reader.read(path)
        settings = cls.model_validate(config_data, strict=strict)
        log.debug("Settings read from path: %s.", path)
        return settings
