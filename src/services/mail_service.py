"""Получение прайсов поставщиков из почты по IMAP."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from domain.config_context import get_config_provider
from domain.mail import ImapClient, PriceDownloadError
from domain.protocols import ConfigProvider
from infrastructure.config.mail_credentials import get_mail_credentials
from infrastructure.mail.download import download_price
from infrastructure.mail.imap import connect, list_price_folders, save_price
from parsers.mail.client import FoundPrice, find_latest_price
from parsers.mail.models import MailConfig
from parsers.mail.provider import load_mail_config
from services.vendor_activity import skip_mail_fetch

logger = logging.getLogger(__name__)

_PRICE_FILENAME = 'price.xlsx'


@dataclass(frozen=True, slots=True)
class MailFetchResult:
    """Результат выгрузки прайса одного поставщика."""

    folder: str
    subject: str
    date: str
    filename: str
    path: str


@dataclass(slots=True)
class _MailSession:
    """Закрывает IMAP-сессию при выходе, даже если выгрузка упала."""

    client: ImapClient

    def __enter__(self) -> ImapClient:
        """Вернуть открытый IMAP-клиент."""
        return self.client

    def __exit__(self, _exc_type: object, _exc_value: object, _traceback: object) -> None:
        """Разлогиниться на выходе из блока."""
        self.client.logout()


class MailService:
    """Скачивает свежие прайсы поставщиков из настроенного почтового ящика."""

    def __init__(self, config_provider: ConfigProvider | None = None) -> None:
        self._config_provider = config_provider

    def fetch_prices(self) -> list[MailFetchResult]:
        """Скачать по одному свежему прайсу на каждый активный профиль."""
        config = load_mail_config(self._config_provider or get_config_provider())
        account = config.account
        client = connect(account.host, account.port, account.folder, get_mail_credentials())
        with _MailSession(client) as inbox:
            folders = list_price_folders(inbox, config.account.folder)
            return _collect(inbox, config, folders)


def _collect(client: ImapClient, config: MailConfig, folders: list[str]) -> list[MailFetchResult]:
    """Обойти активные профили: найти письмо, записать вложение, собрать итог."""
    fetched: list[MailFetchResult] = []
    for folder, profile in config.enabled_profiles().items():
        if skip_mail_fetch(folder):
            continue
        found = find_latest_price(client, folders, profile=profile)
        if found is None:
            logger.warning(f'Для поставщика «{folder}» подходящее письмо не найдено.')
            continue
        saved = _save_found(folder, found)
        if saved is not None:
            fetched.append(saved)
    return fetched


def _save_found(folder: str, found: FoundPrice) -> MailFetchResult | None:
    """Записать прайс поставщика; не скачался по ссылке — None и предупреждение."""
    try:
        payload = _price_payload(found)
    except PriceDownloadError as exc:
        logger.warning(f'Прайс поставщика «{folder}» не скачан: {exc}')
        return None
    destination = _destination(folder)
    save_price(destination, payload)
    return MailFetchResult(
        folder=folder,
        subject=found.subject,
        date=found.date,
        filename=found.filename,
        path=str(destination),
    )


def _price_payload(found: FoundPrice) -> bytes:
    """Байты прайса: вложение письма или файл по ссылке из тела."""
    if found.link is None:
        return found.payload
    return download_price(found.link)


def _destination(folder: str) -> Path:
    """Путь сохранения прайса: file_prices/<папка>/price.xlsx."""
    return Path(get_config_provider().price_folder(folder)) / _PRICE_FILENAME
