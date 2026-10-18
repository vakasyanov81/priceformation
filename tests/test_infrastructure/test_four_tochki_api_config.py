"""Настройки API Форточек из окружения и .env."""

import os
from pathlib import Path

import pytest

from infrastructure.config.fake_config_provider import FakeConfigProvider
from infrastructure.config.four_tochki_api_config import (
    FourTochkiApiConfigError,
    get_four_tochki_api_config,
)

_LOGIN = 'FOUR_TOCHKI_API_LOGIN'
_PASSWORD = 'FOUR_TOCHKI_API_PASSWORD'
_HOST = 'FOUR_TOCHKI_API_HOST'
_WSDL = 'https://api-b2b.4tochki.ru/WCF/ClientService.svc?wsdl'
_SERVICE = 'https://api-b2b.4tochki.ru/WCF/ClientService.svc'


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Окружение без переменных Форточек; load_dotenv пишет в подменённый словарь, а не в os.environ."""
    environ: dict[str, str] = {}
    monkeypatch.setattr(os, 'environ', environ)
    return environ


def test_wsdl_host_is_converted_to_service_endpoint(
    clean_env: dict[str, str],
    fake_config_provider: FakeConfigProvider,
) -> None:
    """В .env указан WSDL-адрес — для вызовов берётся адрес самого сервиса."""
    clean_env.update({_LOGIN: 'user', _PASSWORD: 'pass', _HOST: _WSDL})
    config = get_four_tochki_api_config()
    assert config.endpoint == _SERVICE
    assert (config.login, config.password) == ('user', 'pass')


def test_default_endpoint_without_host(
    clean_env: dict[str, str],
    fake_config_provider: FakeConfigProvider,
) -> None:
    """Адрес не задан — используется адрес сервиса по умолчанию."""
    clean_env.update({_LOGIN: 'user', _PASSWORD: 'pass'})
    assert get_four_tochki_api_config().endpoint == _SERVICE


def test_values_are_read_from_dotenv(
    clean_env: dict[str, str],
    fake_config_provider: FakeConfigProvider,
) -> None:
    """Все три значения берутся из .env проекта."""
    Path(fake_config_provider.project_root, '.env').write_text(
        f'{_LOGIN}=dotenv_user\n{_PASSWORD}=dotenv_pass\n{_HOST}={_WSDL}\n',
        encoding='utf-8',
    )
    config = get_four_tochki_api_config()
    assert (config.login, config.password, config.endpoint) == ('dotenv_user', 'dotenv_pass', _SERVICE)


def test_missing_env_file_message(
    clean_env: dict[str, str],
    fake_config_provider: FakeConfigProvider,
) -> None:
    """Нет .env и нет переменных — сообщение предлагает создать .env."""
    with pytest.raises(FourTochkiApiConfigError, match='Не найден файл'):
        get_four_tochki_api_config()


def test_missing_credentials_message(
    clean_env: dict[str, str],
    fake_config_provider: FakeConfigProvider,
) -> None:
    """.env есть, но логин или пароль пустые — сообщение называет переменные."""
    Path(fake_config_provider.project_root, '.env').write_text(f'{_LOGIN}=user\n{_PASSWORD}=\n', encoding='utf-8')
    with pytest.raises(FourTochkiApiConfigError, match=f'Укажите {_LOGIN} и {_PASSWORD}'):
        get_four_tochki_api_config()
