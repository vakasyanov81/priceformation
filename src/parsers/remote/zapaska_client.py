"""HTTPS client for Zapaska catalog download."""

import traceback
from base64 import b64encode
from contextlib import closing
from http.client import HTTPException, HTTPSConnection
from pathlib import Path

from cfg.zapaska_api import ZapaskaApiConfig, ZapaskaApiConnectionError, get_zapaska_api_config
from core.parse_paths import get_parse_paths

_VENDOR_FOLDER = "zapaska"
_GET_TIRES_URL = "/API/hs/V2/GetTires"
_GET_DISK_URL = "/API/hs/V2/GetDisk"
_TIRE_FILENAME = "tire.json"
_DISK_FILENAME = "disk.json"


def basic_auth(username: str, password: str) -> str:
    """Basic Authorization header value."""
    token = b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"


def get_data(url: str, api_config: ZapaskaApiConfig | None = None) -> str:
    """GET from Zapaska API."""
    resolved = api_config or get_zapaska_api_config()
    try:
        return _request_zapaska(url, resolved)
    except (OSError, HTTPException) as exc:
        raise _zapaska_connection_error(url, resolved.host, exc) from exc


def download_catalogs(*, dest_dir: Path, api: ZapaskaApiConfig | None = None) -> None:
    """GET GetTires / GetDisk → dest_dir/tire.json, disk.json."""
    api_config = api or get_zapaska_api_config()
    dest_dir.mkdir(parents=True, exist_ok=True)
    _write_catalog(dest_dir / _TIRE_FILENAME, get_data(_GET_TIRES_URL, api_config=api_config))
    _write_catalog(dest_dir / _DISK_FILENAME, get_data(_GET_DISK_URL, api_config=api_config))


def load_remote_vendor_data() -> None:
    """Скачать каталоги Запаски в file_prices/zapaska."""
    dest_dir = Path(get_parse_paths().file_prices_folder) / _VENDOR_FOLDER
    download_catalogs(dest_dir=dest_dir)


def _write_catalog(path: Path, payload: str) -> None:
    path.write_text(payload, encoding="utf-8")


def _request_zapaska(url: str, api_config: ZapaskaApiConfig) -> str:
    """Perform GET against Zapaska HTTPS API."""
    with closing(HTTPSConnection(api_config.host)) as connection:
        headers = {"Authorization": basic_auth(api_config.login, api_config.password)}
        connection.request("GET", url, headers=headers)
        return connection.getresponse().read().decode("utf-8")


def _zapaska_connection_error(url: str, host: str, exc: Exception) -> ZapaskaApiConnectionError:
    """Human-readable connection error; original exception goes to logs."""
    detail = f"host={host} url={url}\n{exc!r}\n{traceback.format_exc()}"
    return ZapaskaApiConnectionError(detail=detail)
