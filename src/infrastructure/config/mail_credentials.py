"""Учётные данные почтового ящика: .env / переменные окружения / интерактивный ввод.

Логин и пароль не хранятся в JSON-настройках: они берутся из ``MAIL_LOGIN`` и
``MAIL_PASSWORD`` (переменные сессии или ``.env``), а если чего-то не хватает и
запуск интерактивный — запрашиваются у пользователя.
"""

from __future__ import annotations

import getpass
import os
import sys
from dataclasses import dataclass

from domain.exceptions import CoreExceptionError
from infrastructure.config.dotenv import load_dotenv

_ENV_LOGIN = 'MAIL_LOGIN'
_ENV_PASSWORD = 'MAIL_PASSWORD'  # nosec — имя переменной окружения, а не пароль
_MSG_MISSING = (
    f'Не заданы учётные данные почты. Укажите {_ENV_LOGIN} и {_ENV_PASSWORD} в .env '
    'или введите их в интерактивном режиме.'
)


class MailCredentialsError(CoreExceptionError):
    """Не хватает логина или пароля почтового ящика."""


@dataclass(frozen=True, slots=True)
class MailCredentials:
    """Логин и пароль почтового ящика."""

    login: str
    password: str


def get_mail_credentials() -> MailCredentials:
    """Доступы из .env / окружения; при неполных данных — интерактивный запрос."""
    load_dotenv()
    login = os.environ.get(_ENV_LOGIN, '').strip()
    password = os.environ.get(_ENV_PASSWORD, '').strip()
    if login and password:
        return MailCredentials(login=login, password=password)
    return _resolve_missing(login, password)


def _resolve_missing(login: str, password: str) -> MailCredentials:
    """Дозапросить недостающие данные в терминале; вне терминала — ошибка."""
    if not sys.stdin.isatty():
        raise MailCredentialsError(_MSG_MISSING)
    resolved_login = login or _ask_login()
    resolved_password = password or _ask_password()
    if resolved_login and resolved_password:
        return MailCredentials(login=resolved_login, password=resolved_password)
    raise MailCredentialsError(_MSG_MISSING)


def _ask_login() -> str:
    try:
        return input('Логин почтового ящика: ').strip()
    except (EOFError, KeyboardInterrupt) as exc:
        raise MailCredentialsError(_MSG_MISSING) from exc


def _ask_password() -> str:
    try:
        return getpass.getpass('Пароль почтового ящика: ').strip()
    except (EOFError, KeyboardInterrupt) as exc:
        raise MailCredentialsError(_MSG_MISSING) from exc
