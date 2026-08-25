"""tests for Zapaska HTTPS catalog client"""

from base64 import b64encode
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from cfg.zapaska_api import ZapaskaApiConfig, ZapaskaApiConfigError, ZapaskaApiConnectionError
from core.exceptions import CoreExceptionError
from core.parse_paths import ParsePaths
from parsers.remote.zapaska_client import basic_auth, download_catalogs, get_data, load_remote_vendor_data

_LOGIN = "ZAPASKA_API_LOGIN"
_PASSWORD_ENV = "ZAPASKA_API_PASSWORD"
_TO_LOG = "to_log"
_TEST_USER = "user"
_TEST_SECRET = "secret"
_TEST_HOST = "api.test:443"
_GET_TIRES_URL = "/API/hs/V2/GetTires"
_GET_DISK_URL = "/API/hs/V2/GetDisk"
_HTTPS = "parsers.remote.zapaska_client.HTTPSConnection"
_GET_DATA = "parsers.remote.zapaska_client.get_data"
_API = ZapaskaApiConfig(host=_TEST_HOST, login="u", password=_TEST_SECRET)
_PATHS = ParsePaths(
    file_prices_folder="/prices",
    user_config_folder="/cfg",
    result_folder="/result",
)


def test_basic_auth_header() -> None:
    token = b64encode(f"{_TEST_USER}:{_TEST_SECRET}".encode()).decode()
    assert basic_auth(_TEST_USER, _TEST_SECRET) == f"Basic {token}"


def test_get_data_uses_passed_config() -> None:
    mock_https = _https_mock(body='{"бренд": "x"}'.encode())

    with patch(_HTTPS, mock_https):
        payload = get_data(_GET_TIRES_URL, api_config=_API)

    mock_https.assert_called_once_with(_TEST_HOST)
    connection = mock_https.return_value
    connection.request.assert_called_once_with(
        "GET",
        _GET_TIRES_URL,
        headers={"Authorization": basic_auth("u", _TEST_SECRET)},
    )
    connection.close.assert_called_once()
    assert payload == '{"бренд": "x"}'


def test_get_data_loads_config_when_omitted() -> None:
    mock_https = _https_mock(body=b'{"ok": 1}')

    with (
        patch("parsers.remote.zapaska_client.get_zapaska_api_config", return_value=_API),
        patch(_HTTPS, mock_https),
    ):
        payload = get_data(_GET_TIRES_URL)

    mock_https.assert_called_once_with(_TEST_HOST)
    assert payload == '{"ok": 1}'


def test_get_data_connection_error() -> None:
    mock_https = _https_mock(error=OSError("network down"))

    with (
        patch(_HTTPS, mock_https),
        patch.object(CoreExceptionError, _TO_LOG) as mock_log,
        pytest.raises(ZapaskaApiConnectionError, match="Не удалось подключиться") as raised,
    ):
        get_data(_GET_TIRES_URL, api_config=_API)

    mock_https.return_value.close.assert_called_once()
    mock_log.assert_called_once()
    logged = mock_log.call_args.args[0]
    assert "network down" in logged
    assert _TEST_HOST in logged
    assert _GET_TIRES_URL in logged
    assert "network down" not in str(raised.value)
    assert _TEST_SECRET not in logged
    assert _TEST_SECRET not in str(raised.value)


def test_download_catalogs_writes_tire_and_disk(tmp_path: Path) -> None:
    dest = tmp_path / "nested" / "zapaska"
    payloads = {
        _GET_TIRES_URL: '{"tires": true}',
        _GET_DISK_URL: '{"disks": true}',
    }

    with patch(_GET_DATA, side_effect=lambda url, api_config=None: payloads[url]) as mock_get:
        download_catalogs(dest_dir=dest, api=_API)

    mock_get.assert_any_call(_GET_TIRES_URL, api_config=_API)
    mock_get.assert_any_call(_GET_DISK_URL, api_config=_API)
    assert (dest / "tire.json").read_text(encoding="utf-8") == '{"tires": true}'
    assert (dest / "disk.json").read_text(encoding="utf-8") == '{"disks": true}'


def test_download_catalogs_requires_credentials(tmp_path: Path, monkeypatch: Any) -> None:
    monkeypatch.setattr("cfg.zapaska_api.__PROJECT_ROOT__", str(tmp_path))
    monkeypatch.delenv(_LOGIN, raising=False)
    monkeypatch.delenv(_PASSWORD_ENV, raising=False)
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(ZapaskaApiConfigError):
        download_catalogs(dest_dir=tmp_path / "zapaska")


def test_load_remote_vendor_data_uses_parse_paths() -> None:
    with (
        patch("parsers.remote.zapaska_client.get_parse_paths", return_value=_PATHS),
        patch("parsers.remote.zapaska_client.download_catalogs") as mock_download,
    ):
        load_remote_vendor_data()

    mock_download.assert_called_once_with(dest_dir=Path("/prices") / "zapaska")


def _https_mock(*, body: bytes | None = None, error: Exception | None = None) -> MagicMock:
    mock_cls = MagicMock()
    connection = mock_cls.return_value
    if error is None:
        connection.getresponse.return_value.read.return_value = body
    else:
        connection.request.side_effect = error
    return mock_cls
