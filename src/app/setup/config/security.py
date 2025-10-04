from datetime import timedelta
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class AuthSettings(BaseModel):
    jwt_secret: str = Field(alias="JWT_SECRET", min_length=32)
    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ] = Field(alias="JWT_ALGORITHM")
    session_ttl_min: timedelta = Field(alias="SESSION_TTL_MIN")
    session_refresh_threshold: float = Field(
        gt=0,
        lt=1,
        alias="SESSION_REFRESH_THRESHOLD",
    )

    @field_validator("session_ttl_min", mode="before")
    @classmethod
    def convert_session_ttl_min(cls, v: Any) -> timedelta:
        if not isinstance(v, (int, float)):
            raise ValueError("SESSION_TTL_MIN must be a number (n of minutes, n >= 1).")
        if v < 1:
            raise ValueError("SESSION_TTL_MIN must be at least 1 (n of minutes).")
        return timedelta(minutes=v)


class CookiesSettings(BaseModel):
    secure: bool = Field(alias="SECURE")


class PasswordSettings(BaseModel):
    pepper: str = Field(alias="PEPPER", min_length=32)
    hasher_work_factor: int = Field(alias="HASHER_WORK_FACTOR", ge=10)
    hasher_max_threads: int = Field(alias="HASHER_MAX_THREADS", ge=1)
    hasher_semaphore_wait_timeout_s: float = Field(
        alias="HASHER_SEMAPHORE_WAIT_TIMEOUT_S", gt=0
    )


class SecuritySettings(BaseModel):
    auth: AuthSettings
    cookies: CookiesSettings
    password: PasswordSettings
