"""MIM API access token from environment."""

import os
from dataclasses import dataclass

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv

_DEFAULT_HOST = 'webmim.svrauto.ru'
_ENV_TOKEN = 'MIM_API_TOKEN'  # nosec — имя переменной окружения, а не токен
_ENV_HOST = 'MIM_API_HOST'
_ENV_TYPES = 'MIM_API_TYPES'
# Id категорий МИМ: 1 шины, 2 диски, 3 грузовые шины, 4 грузовые диски, 5 секретки, 6 крепёж, 7 прочее.
_KNOWN_TYPES = frozenset(range(1, 8))
_DEFAULT_TYPES = '1;3;4'
_TYPES_SEPARATORS = ';,'
_MSG_MISSING_ENV_FILE = f'Не найден файл .env с токеном API МИМ. Скопируйте .env.example в .env и укажите {_ENV_TOKEN}.'
_MSG_BAD_TYPES = (
    f'В {_ENV_TYPES} указаны неверные категории МИМ: {{value!r}}. Допустимы id 1–7, через «;» (например, 1;3;4).'
)
_MSG_MISSING_TOKEN = f'В файле .env не задан токен API МИМ. Укажите {_ENV_TOKEN}.'


class MimApiConfigError(CoreExceptionError):
    """Missing MIM API env token."""


@dataclass(frozen=True)
class MimApiConfig:
    """Адрес сервиса и токен доступа к API МИМ."""

    host: str
    token: str
    types: tuple[int, ...]


def get_mim_api_config() -> MimApiConfig:
    """MIM API settings from env / .env."""
    has_env_file = load_dotenv()

    token = os.environ.get(_ENV_TOKEN, '').strip()
    host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST

    if not token:
        raise MimApiConfigError(_token_error_message(has_env_file))

    types = _parse_types(os.environ.get(_ENV_TYPES, ''))
    return MimApiConfig(host=host, token=token, types=types)


def _token_error_message(has_env_file: bool) -> str:
    if has_env_file:
        return _MSG_MISSING_TOKEN
    return _MSG_MISSING_ENV_FILE


def _parse_types(raw: str) -> tuple[int, ...]:
    """Id категорий из «1;3;4»: без дублей, по порядку; пусто — набор по умолчанию."""
    text = raw.strip() or _DEFAULT_TYPES
    for separator in _TYPES_SEPARATORS:
        text = text.replace(separator, ' ')
    parts = text.split()
    if not all(_is_known_type(part) for part in parts):
        raise MimApiConfigError(_MSG_BAD_TYPES.format(value=raw))
    return tuple(dict.fromkeys(int(part) for part in parts))


def _is_known_type(part: str) -> bool:
    return part.isdecimal() and int(part) in _KNOWN_TYPES
