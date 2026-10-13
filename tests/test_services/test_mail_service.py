"""Сервис получения прайсов из почты."""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from log_watch import LoggerWatcher, texts_at

from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail.client import FoundPrice
from parsers.mail.models import MailAccount, MailConfig, MailProfile
from services import mail_service

_ACCOUNT = MailAccount(host='imap.example.ru', port=993, folder='INBOX')
_CREDENTIALS = MailCredentials(login='user', password='secret')
_FOUND = FoundPrice(subject='Прайс', date='01.01.2025 10:00', filename='price.xlsx', payload=b'bytes')


def _profile(sender: str, *, enabled: bool = True) -> MailProfile:
    return MailProfile(
        sender=sender,
        sender_is_domain=False,
        subject_keyword=None,
        attachment_glob='*.xlsx',
        enabled=enabled,
    )


def _wire(
    monkeypatch: pytest.MonkeyPatch,
    config: MailConfig,
    found: FoundPrice | None,
) -> tuple[MagicMock, MagicMock, MagicMock, MagicMock]:
    """Подменить адаптеры сервиса; вернуть connect, find, save и клиент."""
    client = MagicMock()
    connect = MagicMock(return_value=client)
    find = MagicMock(return_value=found)
    save = MagicMock()
    monkeypatch.setattr(mail_service, 'load_mail_config', lambda: config)
    monkeypatch.setattr(mail_service, 'get_mail_credentials', lambda: _CREDENTIALS)
    monkeypatch.setattr(mail_service, 'connect', connect)
    monkeypatch.setattr(mail_service, 'find_latest_price', find)
    monkeypatch.setattr(mail_service, 'save_price', save)
    return connect, find, save, client


def test_fetch_prices_saves_each_enabled_profile(
    fake_config_provider: FakeConfigProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Активные профили сохраняют письмо; выключенный пропускается."""
    config = MailConfig(
        account=_ACCOUNT,
        profiles={'pioner': _profile('a@b.ru'), 'stk': _profile('c@d.ru', enabled=False)},
    )
    connect, find, save, client = _wire(monkeypatch, config, _FOUND)

    fetched = mail_service.MailService().fetch_prices()

    destination = Path(fake_config_provider.price_folder('pioner')) / 'price.xlsx'
    connect.assert_called_once_with(_ACCOUNT, _CREDENTIALS)
    client.logout.assert_called_once()
    find.assert_called_once_with(client, profile=config.profiles['pioner'])
    save.assert_called_once_with(destination, b'bytes')
    entry = fetched[0]
    assert entry.folder == 'pioner'
    assert entry.subject == 'Прайс'
    assert entry.path == str(destination)


def test_fetch_prices_reports_missing_letter(
    watch_logger: LoggerWatcher,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Если письмо не найдено, прайс не пишется, а в лог идёт предупреждение."""
    config = MailConfig(account=_ACCOUNT, profiles={'stk': _profile('c@d.ru')})
    _connect, _find, save, _client = _wire(monkeypatch, config, None)
    entries = watch_logger('services.mail_service')

    assert not mail_service.MailService().fetch_prices()
    save.assert_not_called()
    warnings = texts_at(entries(), logging.WARNING)
    assert len(warnings) == 1
    assert 'stk' in warnings[0]
