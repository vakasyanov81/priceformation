"""Four Tochki (Форточки) SOAP API credentials from environment."""

import os
from dataclasses import dataclass

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv

_DEFAULT_ENDPOINT = 'https://api-b2b.4tochki.ru/WCF/ClientService.svc'
_WSDL_SUFFIX = '?wsdl'
_ENV_LOGIN = 'FOUR_TOCHKI_API_LOGIN'
_ENV_PASSWORD = 'FOUR_TOCHKI_API_PASSWORD'  # nosec — имя переменной окружения, а не пароль
_ENV_HOST = 'FOUR_TOCHKI_API_HOST'
_MSG_MISSING_ENV_FILE = (
    'Не найден файл .env с данными для подключения к API Форточек. '
    'Скопируйте .env.example в .env и укажите логин и пароль.'
)
_MSG_MISSING_CREDENTIALS = (
    f'В файле .env не заданы данные для подключения к API Форточек. Укажите {_ENV_LOGIN} и {_ENV_PASSWORD}.'
)


class FourTochkiApiConfigError(CoreExceptionError):
    """Missing Four Tochki API env credentials."""


@dataclass(frozen=True)
class FourTochkiApiConfig:
    """Адрес SOAP-сервиса и логин с паролем для Форточек."""

    endpoint: str
    login: str
    password: str


def get_four_tochki_api_config() -> FourTochkiApiConfig:
    """Настройки API Форточек из env / .env."""
    has_env_file = load_dotenv()

    login = os.environ.get(_ENV_LOGIN, '').strip()
    password = os.environ.get(_ENV_PASSWORD, '').strip()

    if not login or not password:
        raise FourTochkiApiConfigError(_credentials_error_message(has_env_file))

    endpoint = _endpoint(os.environ.get(_ENV_HOST, ''))
    return FourTochkiApiConfig(endpoint=endpoint, login=login, password=password)


def _endpoint(raw_host: str) -> str:
    """В .env часто указан WSDL-адрес; для SOAP-вызовов нужен сам адрес сервиса."""
    address = raw_host.strip() or _DEFAULT_ENDPOINT
    return address.removesuffix(_WSDL_SUFFIX)


def _credentials_error_message(has_env_file: bool) -> str:
    if has_env_file:
        return _MSG_MISSING_CREDENTIALS
    return _MSG_MISSING_ENV_FILE
