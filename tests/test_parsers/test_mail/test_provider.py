"""Провайдер настроек почты parse_config/mail.json."""

import json
from pathlib import Path

import pytest

from domain.config_context import get_config_provider
from domain.exceptions import ConfigValidationError
from domain.mail import MailConfigNotFoundError
from infrastructure.config.fake_config_provider import FakeConfigProvider
from parsers.mail.provider import clear_mail_config_cache, load_mail_config

_CONFIG = {
    'imap': {'host': 'imap.example.ru'},
    'profiles': {'pioner': {'sender': 'rmv@pionersib.ru', 'attachment_glob': '*.xlsx'}},
}


def _write(provider: FakeConfigProvider, payload: object) -> Path:
    path = Path(provider.config_file('mail.json'))
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    return path


def test_load_mail_config(fake_config_provider: FakeConfigProvider) -> None:
    """Настройки читаются из parse_config/mail.json активного провайдера."""
    _write(fake_config_provider, _CONFIG)
    config = load_mail_config(get_config_provider())
    assert config.account.host == 'imap.example.ru'
    assert config.profiles['pioner'].sender == 'rmv@pionersib.ru'


def test_load_mail_config_cached(fake_config_provider: FakeConfigProvider) -> None:
    """Повторное чтение отдаёт закэшированный объект, пока кэш не сброшен."""
    _write(fake_config_provider, _CONFIG)
    first = load_mail_config(get_config_provider())
    _write(fake_config_provider, {'profiles': {}})
    assert load_mail_config(get_config_provider()) is first
    clear_mail_config_cache()
    assert load_mail_config(get_config_provider()).profiles == {}


def test_missing_file_raises(fake_config_provider: FakeConfigProvider) -> None:
    """Нет файла настроек — понятная ошибка."""
    with pytest.raises(MailConfigNotFoundError, match=r'mail\.json'):
        load_mail_config(get_config_provider())


def test_broken_json_raises(fake_config_provider: FakeConfigProvider) -> None:
    """Нечитаемый JSON — ошибка конфига с именем файла."""
    Path(fake_config_provider.config_file('mail.json')).write_text('{', encoding='utf-8')
    with pytest.raises(ConfigValidationError, match=r'mail\.json'):
        load_mail_config(get_config_provider())


def test_sender_is_taken_from_env(fake_config_provider: FakeConfigProvider, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ссылка ``${…}`` в mail.json заменяется значением из окружения: адрес в файле не хранится."""
    monkeypatch.setenv('MAIL_SENDER_TEST', 'price@supplier.ru')
    _write(fake_config_provider, {'profiles': {'stk': {'sender': '${MAIL_SENDER_TEST}', 'attachment_glob': '*.xlsx'}}})

    assert load_mail_config(get_config_provider()).profiles['stk'].sender == 'price@supplier.ru'


def test_missing_sender_env_names_key(
    fake_config_provider: FakeConfigProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv('MAIL_SENDER_ABSENT', raising=False)
    _write(fake_config_provider, {'profiles': {'stk': {'sender': '${MAIL_SENDER_ABSENT}'}}})

    with pytest.raises(ConfigValidationError, match='profiles → stk → sender: не задана переменная окружения'):
        load_mail_config(get_config_provider())
