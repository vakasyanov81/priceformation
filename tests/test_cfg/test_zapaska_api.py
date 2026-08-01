"""tests for Zapaska API env configuration"""

from unittest.mock import MagicMock, patch

import pytest

from cfg.zapaska_api import ZapaskaApiConfig, ZapaskaApiConfigError, get_zapaska_api_config, load_dotenv
from core.exceptions import CoreExceptionError

_LOGIN = "ZAPASKA_API_LOGIN"
_PASSWORD_ENV = "ZAPASKA_API_PASSWORD"
_HOST = "ZAPASKA_API_HOST"
_TO_LOG = "to_log"
_TEST_USER = "user"
_TEST_SECRET = "secret"
_TEST_HOST = "api.test:443"


def test_config_from_dotenv_file(tmp_path, monkeypatch):
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


def test_config_from_env(monkeypatch):
    monkeypatch.setenv(_LOGIN, _TEST_USER)
    monkeypatch.setenv(_PASSWORD_ENV, _TEST_SECRET)
    monkeypatch.delenv(_HOST, raising=False)

    config = get_zapaska_api_config()

    assert config.login == _TEST_USER
    assert config.password == _TEST_SECRET
    assert config.host == "ka2.sibzapaska.ru:16500"


def test_config_custom_host(monkeypatch):
    monkeypatch.setenv(_LOGIN, _TEST_USER)
    monkeypatch.setenv(_PASSWORD_ENV, _TEST_SECRET)
    monkeypatch.setenv(_HOST, "api.example:443")

    assert get_zapaska_api_config().host == "api.example:443"


def test_config_missing_credentials(monkeypatch):
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    with (
        patch("cfg.zapaska_api.load_dotenv"),
        patch.object(CoreExceptionError, _TO_LOG),
        pytest.raises(ZapaskaApiConfigError),
    ):
        get_zapaska_api_config()


def test_get_data_uses_env_config():
    api_config = ZapaskaApiConfig(host=_TEST_HOST, login="u", password=_TEST_SECRET)
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"ok": 1}'
    mock_conn = MagicMock()
    mock_conn.return_value.getresponse.return_value = mock_response

    with patch("parsers.vendors.zapaska_tire_json.HTTPSConnection", mock_conn):
        from parsers.vendors.zapaska_tire_json import get_data

        payload = get_data("/API/hs/V2/GetTires", api_config=api_config)

    mock_conn.assert_called_once_with(_TEST_HOST)
    mock_conn.return_value.request.assert_called_once()
    assert payload == '{"ok": 1}'
