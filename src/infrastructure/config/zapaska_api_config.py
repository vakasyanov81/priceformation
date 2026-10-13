"""Zapaska API credentials from environment."""

import os
from dataclasses import dataclass

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv

_DEFAULT_HOST = 'ka2.sibzapaska.ru:16500'
_ENV_LOGIN = 'ZAPASKA_API_LOGIN'
_ENV_PASSWORD = 'ZAPASKA_API_PASSWORD'  # nosec — имя переменной окружения, а не пароль
_ENV_HOST = 'ZAPASKA_API_HOST'
_MSG_MISSING_ENV_FILE = (
    'Не найден файл .env с данными для подключения к API Запаски. '
    'Скопируйте .env.example в .env и укажите логин и пароль.'
)
_MSG_MISSING_CREDENTIALS = (
    f'В файле .env не заданы данные для подключения к API Запаски. Укажите {_ENV_LOGIN} и {_ENV_PASSWORD}.'
)


class ZapaskaApiConfigError(CoreExceptionError):
    """Missing Zapaska API env credentials."""


@dataclass(frozen=True)
class ZapaskaApiConfig:
    """connection settings for Zapaska HTTPS API"""

    host: str
    login: str
    password: str


def get_zapaska_api_config() -> ZapaskaApiConfig:
    """Zapaska API settings from env / .env."""
    has_env_file = load_dotenv()

    login = os.environ.get(_ENV_LOGIN, '').strip()
    password = os.environ.get(_ENV_PASSWORD, '').strip()
    host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST

    if not login or not password:
        raise ZapaskaApiConfigError(_credentials_error_message(has_env_file))

    return ZapaskaApiConfig(host=host, login=login, password=password)


def _credentials_error_message(has_env_file: bool) -> str:
    if has_env_file:
        return _MSG_MISSING_CREDENTIALS
    return _MSG_MISSING_ENV_FILE
