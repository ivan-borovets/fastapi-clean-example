from datetime import timedelta
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


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
        if not isinstance(v, (int, float)):
            raise ValueError("SESSION_TTL_MIN must be a number (n of minutes, n >= 1).")
        if v < 1:
            raise ValueError("SESSION_TTL_MIN must be at least 1 (n of minutes).")
        return timedelta(minutes=v)

    @field_validator("session_refresh_threshold", mode="before")
    @classmethod
    def validate_session_refresh_threshold(cls, v: Any) -> float:
        if not isinstance(v, (int, float)):
            raise ValueError(
                "SESSION_REFRESH_THRESHOLD must be a number "
                "(fraction, 0 < fraction < 1).",
            )
        if not 0 < v < 1:
            raise ValueError(
                "SESSION_REFRESH_THRESHOLD must be between 0 and 1, exclusive.",
            )
        return v


class CookiesSettings(BaseModel):
    secure: bool = Field(alias="SECURE")


class PasswordSettings(BaseModel):
    pepper: str = Field(alias="PEPPER")


class SecuritySettings(BaseModel):
    auth: AuthSettings
    cookies: CookiesSettings
    password: PasswordSettings
