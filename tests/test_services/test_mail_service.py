"""Сервис получения прайсов из почты."""

import logging
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from log_watch import LoggerWatcher, texts_at

from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.mail_credentials import MailCredentials
from parsers.mail.client import FoundPrice
from parsers.mail.errors import PriceDownloadError
from parsers.mail.models import MailAccount, MailConfig, MailProfile
from parsers.vendor_config.models import VendorConfig
from services import mail_service

_ACCOUNT = MailAccount(host='imap.example.ru', port=993, folder='INBOX')
_CREDENTIALS = MailCredentials(login='user', password='secret')
_FOUND = FoundPrice(subject='Прайс', date='01.01.2025 10:00', filename='price.xlsx', payload=b'bytes')
_FOLDERS = ['INBOX', 'INBOX.Prices']


@pytest.fixture(autouse=True)
def _no_vendor_configs(monkeypatch: pytest.MonkeyPatch) -> None:
    """По умолчанию конфигов поставщиков нет — почта грузится для всех активных профилей."""
    monkeypatch.setattr('services.vendor_activity.load_vendor_configs', dict)


def _profile(sender: str, *, enabled: bool = True) -> MailProfile:
    return MailProfile(
        sender=sender,
        sender_is_domain=False,
        subject_keyword=None,
        attachment_glob='*.xlsx',
        enabled=enabled,
    )


@dataclass(frozen=True)
class _Wired:
    """Подменённые адаптеры сервиса."""

    connect: MagicMock
    folders: MagicMock
    find: MagicMock
    save: MagicMock
    client: MagicMock


def _wire(
    monkeypatch: pytest.MonkeyPatch,
    config: MailConfig,
    found: FoundPrice | None,
) -> _Wired:
    """Подменить адаптеры сервиса и вернуть их."""
    client = MagicMock()
    wired = _Wired(
        connect=MagicMock(return_value=client),
        folders=MagicMock(return_value=_FOLDERS),
        find=MagicMock(return_value=found),
        save=MagicMock(),
        client=client,
    )
    monkeypatch.setattr(mail_service, 'load_mail_config', lambda: config)
    monkeypatch.setattr(mail_service, 'get_mail_credentials', lambda: _CREDENTIALS)
    monkeypatch.setattr(mail_service, 'connect', wired.connect)
    monkeypatch.setattr(mail_service, 'list_price_folders', wired.folders)
    monkeypatch.setattr(mail_service, 'find_latest_price', wired.find)
    monkeypatch.setattr(mail_service, 'save_price', wired.save)
    return wired


def test_fetch_prices_saves_each_enabled_profile(
    fake_config_provider: FakeConfigProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Активные профили сохраняют письмо; выключенный пропускается."""
    config = MailConfig(
        account=_ACCOUNT,
        profiles={'pioner': _profile('a@b.ru'), 'stk': _profile('c@d.ru', enabled=False)},
    )
    wired = _wire(monkeypatch, config, _FOUND)

    fetched = mail_service.MailService().fetch_prices()

    destination = Path(fake_config_provider.price_folder('pioner')) / 'price.xlsx'
    wired.connect.assert_called_once_with(_ACCOUNT, _CREDENTIALS)
    wired.folders.assert_called_once_with(wired.client, 'INBOX')
    wired.client.logout.assert_called_once()
    wired.find.assert_called_once_with(wired.client, _FOLDERS, profile=config.profiles['pioner'])
    wired.save.assert_called_once_with(destination, b'bytes')
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
    wired = _wire(monkeypatch, config, None)
    entries = watch_logger('services.mail_service')

    assert not mail_service.MailService().fetch_prices()
    wired.save.assert_not_called()
    warnings = texts_at(entries(), logging.WARNING)
    assert len(warnings) == 1
    assert 'stk' in warnings[0]


def test_fetch_prices_continues_after_missing_letter(
    fake_config_provider: FakeConfigProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Профиль без письма в середине списка не останавливает остальные; итог — все поля письма."""
    config = MailConfig(
        account=_ACCOUNT,
        profiles={'pioner': _profile('a@b.ru'), 'stk': _profile('c@d.ru'), 'poshk': _profile('e@f.ru')},
    )
    wired = _wire(monkeypatch, config, _FOUND)
    wired.find.side_effect = [_FOUND, None, _FOUND]

    fetched = mail_service.MailService().fetch_prices()

    assert fetched == [
        mail_service.MailFetchResult(
            folder=folder,
            subject='Прайс',
            date='01.01.2025 10:00',
            filename='price.xlsx',
            path=str(Path(fake_config_provider.price_folder(folder)) / 'price.xlsx'),
        )
        for folder in ('pioner', 'poshk')
    ]


def test_fetch_prices_downloads_by_link(
    fake_config_provider: FakeConfigProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Письмо со ссылкой: прайс скачивается по ссылке и сохраняется."""
    config = MailConfig(account=_ACCOUNT, profiles={'four_tochki': _profile('a@b.ru')})
    link_found = FoundPrice(subject='Остатки', date='01.01.2025', filename='o.xlsx', link='https://x.ru/o.xlsx')
    wired = _wire(monkeypatch, config, link_found)
    downloaded = MagicMock(return_value=b'from-link')
    monkeypatch.setattr(mail_service, 'download_price', downloaded)

    fetched = mail_service.MailService().fetch_prices()

    downloaded.assert_called_once_with('https://x.ru/o.xlsx')
    wired.save.assert_called_once_with(
        Path(fake_config_provider.price_folder('four_tochki')) / 'price.xlsx', b'from-link'
    )
    assert len(fetched) == 1


def test_fetch_prices_skips_failed_download(
    watch_logger: LoggerWatcher,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ошибка скачивания не роняет выгрузку: поставщик пропускается с предупреждением."""
    config = MailConfig(account=_ACCOUNT, profiles={'four_tochki': _profile('a@b.ru')})
    link_found = FoundPrice(subject='Остатки', date='01.01.2025', filename='o.xlsx', link='https://x.ru/o.xlsx')
    wired = _wire(monkeypatch, config, link_found)

    def _fail(_url: str) -> bytes:
        raise PriceDownloadError('сеть недоступна')

    monkeypatch.setattr(mail_service, 'download_price', _fail)
    entries = watch_logger('services.mail_service')

    assert not mail_service.MailService().fetch_prices()
    wired.save.assert_not_called()
    warnings = texts_at(entries(), logging.WARNING)
    assert len(warnings) == 1
    assert 'four_tochki' in warnings[0]


@pytest.mark.parametrize(
    ('enabled', 'source'),
    [(False, 'xlsx'), (True, 'api'), (False, 'api')],
    ids=['vendor-disabled', 'source-api', 'disabled-and-api'],
)
def test_fetch_prices_skips_vendor_not_using_mail(
    monkeypatch: pytest.MonkeyPatch,
    watch_logger: LoggerWatcher,
    *,
    enabled: bool,
    source: str,
) -> None:
    """Поставщик отключён или разбирается по API — письмо для него не ищется."""
    config = MailConfig(account=_ACCOUNT, profiles={'pioner': _profile('a@b.ru')})
    wired = _wire(monkeypatch, config, _FOUND)
    vendor = MagicMock(spec=VendorConfig, enabled=enabled, source=source)
    monkeypatch.setattr('services.vendor_activity.load_vendor_configs', lambda: {'pioner': vendor})
    entries = watch_logger('services.vendor_activity')

    assert not mail_service.MailService().fetch_prices()
    wired.find.assert_not_called()
    wired.save.assert_not_called()
    assert len(texts_at(entries(), logging.INFO)) == 1


def test_fetch_prices_loads_active_file_vendor(
    fake_config_provider: FakeConfigProvider,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Активный поставщик с файловым источником получает прайс из почты."""
    config = MailConfig(account=_ACCOUNT, profiles={'pioner': _profile('a@b.ru')})
    wired = _wire(monkeypatch, config, _FOUND)
    vendor = MagicMock(spec=VendorConfig, enabled=True, source='xlsx')
    monkeypatch.setattr('services.vendor_activity.load_vendor_configs', lambda: {'pioner': vendor})

    assert len(mail_service.MailService().fetch_prices()) == 1
    wired.find.assert_called_once()
