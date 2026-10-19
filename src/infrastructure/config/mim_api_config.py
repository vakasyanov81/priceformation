"""MIM API access token from environment."""

import os
from dataclasses import dataclass

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv

_DEFAULT_HOST = 'webmim.svrauto.ru'
_ENV_TOKEN = 'MIM_API_TOKEN'  # nosec — имя переменной окружения, а не токен
_ENV_HOST = 'MIM_API_HOST'
_MSG_MISSING_ENV_FILE = f'Не найден файл .env с токеном API МИМ. Скопируйте .env.example в .env и укажите {_ENV_TOKEN}.'
_MSG_MISSING_TOKEN = f'В файле .env не задан токен API МИМ. Укажите {_ENV_TOKEN}.'


class MimApiConfigError(CoreExceptionError):
    """Missing MIM API env token."""


@dataclass(frozen=True)
class MimApiConfig:
    """Адрес сервиса и токен доступа к API МИМ."""

    host: str
    token: str


def get_mim_api_config() -> MimApiConfig:
    """MIM API settings from env / .env."""
    has_env_file = load_dotenv()

    token = os.environ.get(_ENV_TOKEN, '').strip()
    host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST

    if not token:
        raise MimApiConfigError(_token_error_message(has_env_file))

    return MimApiConfig(host=host, token=token)


def _token_error_message(has_env_file: bool) -> str:
    if has_env_file:
        return _MSG_MISSING_TOKEN
    return _MSG_MISSING_ENV_FILE
