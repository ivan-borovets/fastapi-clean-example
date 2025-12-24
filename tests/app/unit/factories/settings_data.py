from typing import Literal, TypedDict


class AuthSettingsData(TypedDict):
    JWT_SECRET: str
    JWT_ALGORITHM: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ]
    SESSION_TTL_MIN: int | float
    SESSION_REFRESH_THRESHOLD: int | float


class PostgresSettingsData(TypedDict):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str
    PORT: int
    DRIVER: str


def create_auth_settings_data(
    jwt_secret: str = "jwt_secret" + "0" * 32,
    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "RS256",
        "RS384",
        "RS512",
    ] = "RS256",
    session_ttl_min: int | float = 2,
    session_refresh_threshold: int | float = 0.5,
) -> AuthSettingsData:
    return AuthSettingsData(
        JWT_SECRET=jwt_secret,
        JWT_ALGORITHM=jwt_algorithm,
        SESSION_TTL_MIN=session_ttl_min,
        SESSION_REFRESH_THRESHOLD=session_refresh_threshold,
    )


def create_postgres_settings_data(
    user: str = "user",
    password: str = "password",
    db: str = "db",
    host: str = "localhost",
    port: int = 5432,
    driver: str = "asyncpg",
) -> PostgresSettingsData:
    return PostgresSettingsData(
        USER=user,
        PASSWORD=password,
        DB=db,
        HOST=host,
        PORT=port,
        DRIVER=driver,
    )
