"""HTTPS client for MIM catalog download."""

import gzip
from contextlib import closing
from http import HTTPStatus
from http.client import HTTPException, HTTPSConnection
from pathlib import Path
from typing import Protocol
from urllib.parse import urlencode

from domain.config_context import get_config_provider
from domain.exceptions import CoreExceptionError

_VENDOR_FOLDER = 'mim'
_UNLOAD_PATH = '/api/v1/catalog/unload'
_CATALOG_FILENAME = 'price.xlsx'
_TERRITORIES_PATH = '/goods/unload/territories-list'
_TERRITORIES_FILENAME = 'territories.json'
_FORMAT = 'xlsx'
_GZIP_MAGIC = b'\x1f\x8b'
_TYPES_SEPARATOR = ';'
_TIMEOUT_SECONDS = 300
_MSG_CONNECTION_FAILED = 'Не удалось подключиться к API МИМ. Проверьте интернет-соединение и параметры подключения.'
_MSG_BAD_STATUS = 'API МИМ вернул ошибку. Проверьте токен MIM_API_TOKEN в файле .env.'


class MimApiAuth(Protocol):
    """Host and access token for MIM HTTPS."""

    @property
    def host(self) -> str: ...

    @property
    def token(self) -> str: ...

    @property
    def types(self) -> tuple[int, ...]: ...


class MimApiConnectionError(CoreExceptionError):
    """MIM API host is unreachable."""

    __MESSAGE__ = _MSG_CONNECTION_FAILED


class MimApiResponseError(CoreExceptionError):
    """MIM API answered with a non-OK status."""

    __MESSAGE__ = _MSG_BAD_STATUS


def get_catalog(api_config: MimApiAuth) -> bytes:
    """GET catalog/unload (xlsx, gzip) from MIM API."""
    query = urlencode(
        {
            'access-token': api_config.token,
            'format': _FORMAT,
            'gzip': 'true',
            'types': _TYPES_SEPARATOR.join(str(type_id) for type_id in api_config.types),
        },
    )
    body = _get(api_config, _UNLOAD_PATH, query)
    # gzip=true: сервер отдаёт сжатое тело; обычный ответ (например, без сжатия) возвращаем как есть
    return gzip.decompress(body) if body.startswith(_GZIP_MAGIC) else body


def get_territories(api_config: MimApiAuth) -> bytes:
    """GET goods/unload/territories-list: склады МИМ (id, name, type, address)."""
    return _get(api_config, _TERRITORIES_PATH, urlencode({'token': api_config.token}))


def download_catalog(*, dest_dir: Path, api: MimApiAuth) -> None:
    """GET catalog/unload и список складов → dest_dir/price.xlsx, territories.json.

    Файлы пишутся только после успешных обоих запросов: сбой не оставит прайс без списка складов.
    """
    body = get_catalog(api)
    territories = get_territories(api)
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / _CATALOG_FILENAME).write_bytes(body)
    (dest_dir / _TERRITORIES_FILENAME).write_bytes(territories)


def load_remote_vendor_data(*, api: MimApiAuth) -> None:
    """Скачать каталог МИМ в file_prices/mim."""
    dest_dir = Path(get_config_provider().price_folder(_VENDOR_FOLDER))
    download_catalog(dest_dir=dest_dir, api=api)


def _get(api_config: MimApiAuth, path: str, query: str) -> bytes:
    """GET path?query; токен лежит в query-строке, поэтому в детали ошибок идут только хост и путь."""
    try:
        with closing(HTTPSConnection(api_config.host, timeout=_TIMEOUT_SECONDS)) as connection:
            connection.request('GET', f'{path}?{query}')
            response = connection.getresponse()
            status, body = response.status, response.read()
    except (OSError, HTTPException) as exc:
        raise MimApiConnectionError(detail=f'host={api_config.host} url={path}\n{exc!r}') from exc
    if status != HTTPStatus.OK:
        raise MimApiResponseError(detail=f'host={api_config.host} url={path} status={status}')
    return body
