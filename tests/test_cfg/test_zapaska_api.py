"""tests for Zapaska API env configuration"""

import os
from typing import Any
from unittest.mock import patch

import pytest

from cfg.zapaska_api import (
    ZapaskaApiConfigError,
    get_zapaska_api_config,
    load_dotenv,
)
from core.exceptions import CoreExceptionError

_LOGIN = "ZAPASKA_API_LOGIN"
_PASSWORD_ENV = "ZAPASKA_API_PASSWORD"
_HOST = "ZAPASKA_API_HOST"
_TO_LOG = "to_log"
_TEST_USER = "user"
_TEST_SECRET = "secret"
_DOTENV_KEY = "ZAPASKA_DOTENV_TEST"


def test_config_from_dotenv_file(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    monkeypatch.delenv(_HOST, raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        f"{_LOGIN}={_TEST_USER}\n{_PASSWORD_ENV}={_TEST_SECRET}\n{_HOST}=host.from.env\n",
        encoding="utf-8",
    )

    load_dotenv(env_file)
    config = get_zapaska_api_config()

    assert config.login == _TEST_USER
    assert config.password == _TEST_SECRET
    assert config.host == "host.from.env"


def test_config_from_env(monkeypatch: Any) -> None:
    monkeypatch.setenv(_LOGIN, _TEST_USER)
    monkeypatch.setenv(_PASSWORD_ENV, _TEST_SECRET)
    monkeypatch.delenv(_HOST, raising=False)

    config = get_zapaska_api_config()

    assert config.login == _TEST_USER
    assert config.password == _TEST_SECRET
    assert config.host == "ka2.sibzapaska.ru:16500"


def test_config_custom_host(monkeypatch: Any) -> None:
    monkeypatch.setenv(_LOGIN, _TEST_USER)
    monkeypatch.setenv(_PASSWORD_ENV, _TEST_SECRET)
    monkeypatch.setenv(_HOST, "api.example:443")

    assert get_zapaska_api_config().host == "api.example:443"


def test_config_missing_env_file(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(ZapaskaApiConfigError, match=r"Не найден файл \.env"):
        get_zapaska_api_config()


def test_config_env_file_without_credentials(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    (tmp_path / ".env").write_text("# no credentials\n", encoding="utf-8")
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(ZapaskaApiConfigError, match="не заданы данные"):
        get_zapaska_api_config()


def test_config_login_without_password(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.setenv(_LOGIN, _TEST_USER)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    (tmp_path / ".env").write_text(f"{_LOGIN}={_TEST_USER}\n", encoding="utf-8")
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(ZapaskaApiConfigError, match="не заданы данные"):
        get_zapaska_api_config()


def test_config_password_without_login(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.setenv(_PASSWORD_ENV, _TEST_SECRET)
    (tmp_path / ".env").write_text(f"{_PASSWORD_ENV}={_TEST_SECRET}\n", encoding="utf-8")
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(ZapaskaApiConfigError, match="не заданы данные"):
        get_zapaska_api_config()


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (f'{_DOTENV_KEY}="quoted"', "quoted"),
        (f"{_DOTENV_KEY}='quoted'", "quoted"),
        (f"{_DOTENV_KEY}=a=b", "a=b"),
    ],
)
def test_dotenv_parses_value(tmp_path: Any, monkeypatch: Any, line: str, expected: str) -> None:
    monkeypatch.delenv(_DOTENV_KEY, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(f"{line}\n", encoding="utf-8")

    load_dotenv(env_file)

    assert os.environ[_DOTENV_KEY] == expected


def test_dotenv_skips_invalid_lines(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.delenv(_DOTENV_KEY, raising=False)
    commented_key = f"# {_DOTENV_KEY}"
    env_file = tmp_path / ".env"
    env_lines = [
        "   ",
        f"{commented_key}=from-comment",
        f"={_TEST_USER}",
        "ORPHAN",
        f"{_DOTENV_KEY}={_TEST_SECRET}",
    ]
    env_file.write_text("\n".join(env_lines), encoding="utf-8")

    load_dotenv(env_file)

    assert os.environ[_DOTENV_KEY] == _TEST_SECRET
    assert commented_key not in os.environ
    assert "" not in os.environ


def test_load_dotenv_default_filename(tmp_path: Any, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.delenv(_DOTENV_KEY, raising=False)
    (tmp_path / ".ENV").write_text(f"{_DOTENV_KEY}=from-upper\n", encoding="utf-8")
    (tmp_path / ".env").write_text(f"{_DOTENV_KEY}=from-lower\n", encoding="utf-8")

    load_dotenv()

    assert os.environ[_DOTENV_KEY] == "from-lower"
