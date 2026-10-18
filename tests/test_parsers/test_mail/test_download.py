"""Скачивание прайса по ссылке из письма."""

import io
from typing import Any
from urllib.error import URLError

import pytest

from parsers.mail import download
from parsers.mail.errors import PriceDownloadError


def _open_ok(*_args: Any, **_kwargs: Any) -> io.BytesIO:
    return io.BytesIO(b'xlsx-bytes')


def _open_fail(*_args: Any, **_kwargs: Any) -> None:
    raise URLError('нет сети')


def test_download_price_returns_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Содержимое ответа возвращается как есть."""
    monkeypatch.setattr('urllib.request.urlopen', _open_ok)
    assert download.download_price('https://x.ru/p.xlsx') == b'xlsx-bytes'


def test_download_price_rejects_non_http() -> None:
    """Ссылки не http(s) не скачиваются."""
    with pytest.raises(PriceDownloadError, match='http'):
        download.download_price('file:///etc/passwd')


def test_download_price_wraps_network_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Сетевой сбой превращается в PriceDownloadError с адресом."""
    monkeypatch.setattr('urllib.request.urlopen', _open_fail)
    with pytest.raises(PriceDownloadError, match='Не удалось скачать'):
        download.download_price('https://x.ru/p.xlsx')


def test_download_price_passes_url_and_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Адрес из письма и минутный таймаут доходят до urlopen."""
    calls: list[tuple[Any, ...]] = []

    def _record(*args: Any, **kwargs: Any) -> io.BytesIO:
        calls.append((args, kwargs))
        return io.BytesIO(b'')

    monkeypatch.setattr('urllib.request.urlopen', _record)
    download.download_price('https://x.ru/p.xlsx')

    assert calls == [(('https://x.ru/p.xlsx',), {'timeout': 60})]
