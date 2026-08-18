"""Zapaska API credentials from environment."""

import os
from dataclasses import dataclass
from pathlib import Path

from cfg.main import __PROJECT_ROOT__
from core.exceptions import CoreExceptionError

_DEFAULT_HOST = "ka2.sibzapaska.ru:16500"
_ENV_LOGIN = "ZAPASKA_API_LOGIN"
_ENV_PASSWORD = "ZAPASKA_API_PASSWORD"
_ENV_HOST = "ZAPASKA_API_HOST"
_MSG_MISSING_ENV_FILE = (
    "Не найден файл .env с данными для подключения к API Запаски. "
    "Скопируйте .env.example в .env и укажите логин и пароль."
)
_MSG_MISSING_CREDENTIALS = (
    f"В файле .env не заданы данные для подключения к API Запаски. Укажите {_ENV_LOGIN} и {_ENV_PASSWORD}."
)
_MSG_CONNECTION_FAILED = "Не удалось подключиться к API Запаски. Проверьте интернет-соединение и параметры подключения."


class ZapaskaApiConfigError(CoreExceptionError):
    """Missing Zapaska API env credentials."""


class ZapaskaApiConnectionError(CoreExceptionError):
    """Zapaska API host is unreachable."""

    __MESSAGE__ = _MSG_CONNECTION_FAILED


@dataclass(frozen=True)
class ZapaskaApiConfig:
    """connection settings for Zapaska HTTPS API"""

    host: str
    login: str
    password: str


def _parse_dotenv_line(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, _, raw_value = line.partition("=")
    key = key.strip()
    if not key:
        return None
    return key, raw_value.strip().strip("'").strip('"')


def load_dotenv(env_path: Path | None = None) -> bool:
    """Load .env into os.environ (does not override existing keys)."""
    path = env_path or Path(__PROJECT_ROOT__) / ".env"
    if not path.is_file():
        return False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_dotenv_line(raw_line)
        if parsed is None:
            continue
        key, env_value = parsed
        if key not in os.environ:
            os.environ[key] = env_value
    return True


def get_zapaska_api_config() -> ZapaskaApiConfig:
    """Zapaska API settings from env / .env."""
    has_env_file = load_dotenv()

    login = os.environ.get(_ENV_LOGIN, "").strip()
    password = os.environ.get(_ENV_PASSWORD, "").strip()
    host = os.environ.get(_ENV_HOST, _DEFAULT_HOST).strip() or _DEFAULT_HOST

    if not login or not password:
        raise ZapaskaApiConfigError(_credentials_error_message(has_env_file))

    return ZapaskaApiConfig(host=host, login=login, password=password)


def _credentials_error_message(has_env_file: bool) -> str:
    if has_env_file:
        return _MSG_MISSING_CREDENTIALS
    return _MSG_MISSING_ENV_FILE
