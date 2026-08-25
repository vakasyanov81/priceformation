"""HTTPS client for Zapaska catalog download."""

import traceback
from base64 import b64encode
from contextlib import closing
from http.client import HTTPException, HTTPSConnection
from pathlib import Path
from typing import Protocol

from core.exceptions import CoreExceptionError
from core.parse_paths import get_parse_paths

_VENDOR_FOLDER = "zapaska"
_GET_TIRES_URL = "/API/hs/V2/GetTires"
_GET_DISK_URL = "/API/hs/V2/GetDisk"
_TIRE_FILENAME = "tire.json"
_DISK_FILENAME = "disk.json"
_MSG_CONNECTION_FAILED = "Не удалось подключиться к API Запаски. Проверьте интернет-соединение и параметры подключения."


class ZapaskaApiAuth(Protocol):
    """Host and Basic-auth credentials for Zapaska HTTPS."""

    @property
    def host(self) -> str: ...

    @property
    def login(self) -> str: ...

    @property
    def password(self) -> str: ...


class ZapaskaApiConnectionError(CoreExceptionError):
    """Zapaska API host is unreachable."""

    __MESSAGE__ = _MSG_CONNECTION_FAILED


def basic_auth(username: str, password: str) -> str:
    """Basic Authorization header value."""
    token = b64encode(f"{username}:{password}".encode()).decode("ascii")
    return f"Basic {token}"


def get_data(url: str, api_config: ZapaskaApiAuth) -> str:
    """GET from Zapaska API."""
    try:
        return _request_zapaska(url, api_config)
    except (OSError, HTTPException) as exc:
        detail = f"host={api_config.host} url={url}\n{exc!r}\n{traceback.format_exc()}"
        raise ZapaskaApiConnectionError(detail=detail) from exc


def download_catalogs(*, dest_dir: Path, api: ZapaskaApiAuth) -> None:
    """GET GetTires / GetDisk → dest_dir/tire.json, disk.json."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / _TIRE_FILENAME).write_text(get_data(_GET_TIRES_URL, api_config=api), encoding="utf-8")
    (dest_dir / _DISK_FILENAME).write_text(get_data(_GET_DISK_URL, api_config=api), encoding="utf-8")


def load_remote_vendor_data(*, api: ZapaskaApiAuth) -> None:
    """Скачать каталоги Запаски в file_prices/zapaska."""
    dest_dir = Path(get_parse_paths().file_prices_folder) / _VENDOR_FOLDER
    download_catalogs(dest_dir=dest_dir, api=api)


def _request_zapaska(url: str, api_config: ZapaskaApiAuth) -> str:
    """Perform GET against Zapaska HTTPS API."""
    with closing(HTTPSConnection(api_config.host)) as connection:
        headers = {"Authorization": basic_auth(api_config.login, api_config.password)}
        connection.request("GET", url, headers=headers)
        return connection.getresponse().read().decode("utf-8")
