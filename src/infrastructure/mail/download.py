"""Скачивание прайса по ссылке из тела письма."""

import urllib.request
from urllib.parse import urlsplit

from domain.mail import PriceDownloadError

_TIMEOUT_SECONDS = 60
_ALLOWED_SCHEMES = ('http', 'https')


def download_price(url: str) -> bytes:
    """Содержимое файла по ссылке; только http(s), иначе или при сбое — PriceDownloadError."""
    if urlsplit(url).scheme not in _ALLOWED_SCHEMES:
        raise PriceDownloadError(f'Ссылка на прайс должна быть http(s): {url}')
    try:
        # Схема проверена выше: открываются только http(s)-ссылки из письма.
        with urllib.request.urlopen(url, timeout=_TIMEOUT_SECONDS) as response:  # noqa: S310  # nosec B310
            price: bytes = response.read()
            return price
    except (OSError, ValueError) as exc:
        raise PriceDownloadError(f'Не удалось скачать прайс {url}: {exc}') from exc
