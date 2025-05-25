import copy

import pytest


@pytest.fixture
def password_settings_config_dict_valid():
    return {
        "PEPPER": "Chili",
    }


@pytest.fixture
def auth_settings_config_dict_valid():
    return {
        "JWT_SECRET": "test_secret",
        "JWT_ALGORITHM": "HS256",
        "SESSION_TTL_MIN": 2,
        "SESSION_REFRESH_THRESHOLD": 0.5,
    }


@pytest.fixture
def cookies_settings_config_dict_valid():
    return {
        "SECURE": True,
    }


@pytest.fixture
def security_settings_config_dict_valid(
    password_settings_config_dict_valid,
    auth_settings_config_dict_valid,
    cookies_settings_config_dict_valid,
):
    return {
        "password": password_settings_config_dict_valid,
        "auth": auth_settings_config_dict_valid,
        "cookies": cookies_settings_config_dict_valid,
    }


@pytest.fixture
def postgres_settings_config_dict_valid():
    return {
        "USER": "test_user",
        "PASSWORD": "test_password",
        "DB": "test_db",
        "HOST": "test_host",
        "PORT": 1234,
        "DRIVER": "asyncpg",
    }


@pytest.fixture
def sqla_engine_settings_config_dict_valid():
    return {
        "ECHO": False,
        "ECHO_POOL": False,
        "POOL_SIZE": 10,
        "MAX_OVERFLOW": 10,
    }


@pytest.fixture
def logging_settings_config_dict_valid():
    return {
        "LEVEL": "CRITICAL",
    }


@pytest.fixture
def app_settings_config_dict_valid(
    postgres_settings_config_dict_valid,
    sqla_engine_settings_config_dict_valid,
    security_settings_config_dict_valid,
    logging_settings_config_dict_valid,
):
    return {
        "postgres": postgres_settings_config_dict_valid,
        "sqla": sqla_engine_settings_config_dict_valid,
        "security": security_settings_config_dict_valid,
        "logs": logging_settings_config_dict_valid,
    }


@pytest.fixture
def app_settings_config_dict_invalid(app_settings_config_dict_valid):
    config = copy.deepcopy(app_settings_config_dict_valid)
    config.pop("sqla")
    return config
