"""Получение прайсов поставщиков из почты по IMAP."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from domain.config_context import get_config_provider
from infrastructure.config.mail_credentials import get_mail_credentials
from parsers.mail.client import connect, find_latest_price, list_price_folders, save_price
from parsers.mail.models import MailConfig
from parsers.mail.protocols import ImapClient
from parsers.mail.provider import load_mail_config

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

    def fetch_prices(self) -> list[MailFetchResult]:
        """Скачать по одному свежему прайсу на каждый активный профиль."""
        config = load_mail_config()
        client = connect(config.account, get_mail_credentials())
        with _MailSession(client) as inbox:
            folders = list_price_folders(inbox, config.account.folder)
            return _collect(inbox, config, folders)


def _collect(client: ImapClient, config: MailConfig, folders: list[str]) -> list[MailFetchResult]:
    """Обойти активные профили: найти письмо, записать вложение, собрать итог."""
    fetched: list[MailFetchResult] = []
    for folder, profile in config.enabled_profiles().items():
        found = find_latest_price(client, folders, profile=profile)
        if found is None:
            logger.warning(f'Для поставщика «{folder}» подходящее письмо не найдено.')
            continue
        destination = _destination(folder)
        save_price(destination, found.payload)
        fetched.append(
            MailFetchResult(
                folder=folder,
                subject=found.subject,
                date=found.date,
                filename=found.filename,
                path=str(destination),
            ),
        )
    return fetched


def _destination(folder: str) -> Path:
    """Путь сохранения прайса: file_prices/<папка>/price.xlsx."""
    return Path(get_config_provider().price_folder(folder)) / _PRICE_FILENAME
