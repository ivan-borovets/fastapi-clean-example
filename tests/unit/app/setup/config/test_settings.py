import copy
import os
from datetime import timedelta
from enum import StrEnum
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import PostgresDsn, ValidationError

from app.setup.config.constants import ValidEnvs
from app.setup.config.settings import (
    AppSettings,
    AuthSettings,
    PostgresSettings,
    get_current_env,
    load_full_config,
    load_settings,
    merge_dicts,
    read_config,
    validate_env,
)


@pytest.mark.parametrize(
    (
        "session_ttl_min",
        "session_refresh_threshold",
        "expected_exception",
    ),
    [
        pytest.param(2, 0.5, None, id="init_correct"),
        pytest.param("2", 0.5, ValueError, id="ttl_min_wrong_type"),
        pytest.param(-0.01, 0.5, ValueError, id="ttl_min_too_small"),
        pytest.param(2, "0.5", ValueError, id="session_refresh_threshold_wrong_type"),
        pytest.param(2, -0.01, ValueError, id="session_refresh_threshold_too_small"),
        pytest.param(2, 1.01, ValueError, id="session_refresh_threshold_too_big"),
    ],
)
def test_auth_settings(session_ttl_min, session_refresh_threshold, expected_exception):
    data = {
        "JWT_SECRET": "test_secret",
        "JWT_ALGORITHM": "HS256",
        "SESSION_TTL_MIN": session_ttl_min,
        "SESSION_REFRESH_THRESHOLD": session_refresh_threshold,
    }

    if not expected_exception:
        auth_settings = AuthSettings.model_validate(data)

        assert isinstance(auth_settings, AuthSettings)
        assert auth_settings.session_ttl_min == timedelta(minutes=session_ttl_min)
        assert auth_settings.session_refresh_threshold == session_refresh_threshold

    else:
        with pytest.raises(expected_exception):
            AuthSettings.model_validate(data)


def test_postgres_settings_init_correct():
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("POSTGRES_HOST", None)
        user = "test_user"
        password = "test_password"
        db = "test_db"
        host = "test_host"
        port = 1234
        driver = "asyncpg"

        postgres_settings = PostgresSettings.model_validate({
            "USER": user,
            "PASSWORD": password,
            "DB": db,
            "HOST": host,
            "PORT": port,
            "DRIVER": driver,
        })

        assert isinstance(postgres_settings, PostgresSettings)
        assert postgres_settings.user == user
        assert postgres_settings.password == password
        assert postgres_settings.db == db
        assert postgres_settings.host == host
        assert postgres_settings.port == port
        assert postgres_settings.driver == driver
        assert postgres_settings.dsn == str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}",
                username=user,
                password=password,
                host=host,
                port=port,
                path=db,
            )
        )


def test_postgres_settings_override_host_from_env():
    env_host = "env_host"
    input_host = "input_host"
    data = {
        "USER": "test_user",
        "PASSWORD": "test_password",
        "DB": "test_db",
        "HOST": input_host,
        "PORT": 1234,
        "DRIVER": "asyncpg",
    }

    with patch.dict(os.environ, {"POSTGRES_HOST": env_host}):
        postgres_settings = PostgresSettings.model_validate(data)

        assert postgres_settings.host == env_host

    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("POSTGRES_HOST", None)

        postgres_settings = PostgresSettings.model_validate(data)

        assert postgres_settings.host == input_host


@pytest.mark.parametrize(
    "port",
    [
        pytest.param(0, id="port_too_small"),
        pytest.param(65536, id="port_too_big"),
    ],
)
def test_postgres_settings_field_validator(port):
    with pytest.raises(ValueError), patch.dict(os.environ, {}, clear=False):
        PostgresSettings.model_validate({
            "USER": "test_user",
            "PASSWORD": "test_password",
            "DB": "test_db",
            "HOST": "test_host",
            "PORT": port,
            "DRIVER": "asyncpg",
        })


@pytest.mark.parametrize(
    ("env", "expected_exception"),
    [
        pytest.param(ValidEnvs.LOCAL, None, id="env_correct"),
        pytest.param(None, ValueError, id="env_none"),
        pytest.param("INCORRECT", ValueError, id="env_incorrect"),
    ],
)
def test_validate_env(env, expected_exception):
    if not expected_exception:
        assert validate_env(env=env) == env

    else:
        with pytest.raises(ValueError):
            validate_env(env=env)


def test_read_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[database]\nUSER = "test_postgres"\nPORT = 1234\n')

    with patch("app.setup.config.settings.ENV_TO_DIR_PATHS", {ValidEnvs.DEV: tmp_path}):
        result = read_config(env=ValidEnvs.DEV)

        assert result == {"database": {"USER": "test_postgres", "PORT": 1234}}

    with patch(
        "app.setup.config.settings.ENV_TO_DIR_PATHS",
        {ValidEnvs.DEV: Path("wrong_path"), ValidEnvs.PROD: None},
    ):
        with pytest.raises(FileNotFoundError):
            read_config(env=ValidEnvs.DEV)

        with pytest.raises(FileNotFoundError):
            read_config(env=ValidEnvs.PROD)


@pytest.mark.parametrize(
    ("dict1", "dict2", "result"),
    [
        pytest.param(
            {"a": 1, "b": 2},
            {"b": 3, "c": 4},
            {"a": 1, "b": 3, "c": 4},
            id="flat",
        ),
        pytest.param(
            {"a": 1, "b": {"x": 1, "y": 2}},
            {"b": {"y": 3, "z": 4}, "c": 5},
            {"a": 1, "b": {"x": 1, "y": 3, "z": 4}, "c": 5},
            id="nested",
        ),
    ],
)
def test_merge_dicts(dict1, dict2, result):
    assert merge_dicts(dict1=dict1, dict2=dict2) == result


def test_merge_dicts_keep_original():
    original_dict1 = {"a": 1}
    original_dict2 = {"b": 2}

    merge_dicts(dict1=original_dict1, dict2=original_dict2)

    assert original_dict1 == {"a": 1}
    assert original_dict2 == {"b": 2}


def test_load_full_config(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text('[database]\nUSER = "test_postgres"\nPORT = 1234\n')
    secrets_file = tmp_path / ".secrets.toml"
    secrets_file.write_text(
        '[database]\nPASSWORD = "secret"\n[api]\nKEY = "apikey123"\n',
    )

    with patch("app.setup.config.settings.ENV_TO_DIR_PATHS", {ValidEnvs.DEV: tmp_path}):
        result = load_full_config(env=ValidEnvs.DEV)

        assert result == {
            "database": {"USER": "test_postgres", "PORT": 1234, "PASSWORD": "secret"},
            "api": {"KEY": "apikey123"},
        }

        secrets_file.unlink()

        result_no_secrets = load_full_config(env=ValidEnvs.DEV)

        assert result_no_secrets == {
            "database": {"USER": "test_postgres", "PORT": 1234}
        }


def test_load_settings_with_env_correct(app_settings_config_dict_valid):
    valid_env = ValidEnvs.LOCAL

    with patch("app.setup.config.settings.load_full_config") as mock:
        mock.return_value = app_settings_config_dict_valid

        settings = load_settings(valid_env)

    assert isinstance(settings, AppSettings)

    actual = settings.model_dump(by_alias=True)
    expected = copy.deepcopy(app_settings_config_dict_valid)
    expected["security"]["auth"]["SESSION_TTL_MIN"] = timedelta(
        minutes=expected["security"]["auth"]["SESSION_TTL_MIN"]
    )

    assert actual == expected


def test_load_settings_without_env_correct(app_settings_config_dict_valid):
    valid_env = ValidEnvs.LOCAL

    with (
        patch("app.setup.config.settings.get_current_env") as mock_get_env,
        patch("app.setup.config.settings.load_full_config") as mock_load_config,
    ):
        mock_get_env.return_value = valid_env
        mock_load_config.return_value = app_settings_config_dict_valid

        settings = load_settings()

    assert isinstance(settings, AppSettings)

    actual = settings.model_dump(by_alias=True)
    expected = copy.deepcopy(app_settings_config_dict_valid)
    expected["security"]["auth"]["SESSION_TTL_MIN"] = timedelta(
        minutes=expected["security"]["auth"]["SESSION_TTL_MIN"]
    )

    assert actual == expected


def test_load_settings_without_configuration():
    valid_env = ValidEnvs.LOCAL

    with patch("app.setup.config.settings.load_full_config") as mock:
        mock.return_value = {}

        with pytest.raises(ValidationError):
            load_settings(valid_env)


def test_get_current_env():
    test_app_env_key = "TEST_APP_ENV_KEY"
    test_app_env_value = "TEST_APP_ENV_VALUE"

    class TestValidEnvs(StrEnum):
        test_app_env_key = test_app_env_value

    with (
        patch("app.setup.config.settings.ENV_VAR_NAME", test_app_env_key),
        patch.dict(os.environ, {test_app_env_key: test_app_env_value}),
        patch("app.setup.config.settings.ValidEnvs", TestValidEnvs),
    ):
        assert get_current_env() == test_app_env_value


def test_load_settings_invalid_config_dict_structure(app_settings_config_dict_invalid):
    valid_env = ValidEnvs.LOCAL

    with patch("app.setup.config.settings.load_full_config") as mock:
        mock.return_value = app_settings_config_dict_invalid

        with pytest.raises(ValidationError):
            load_settings(valid_env)
