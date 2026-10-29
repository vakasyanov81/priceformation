"""Запись сообщений об исключениях домена в лог инфраструктуры."""

import logging

from infrastructure.logging.console import FILE_ONLY

logger = logging.getLogger(__name__)
_LOGGED_FLAG = '_traceback_logged'


def write_exception_log(message: str) -> None:
    """Писать в лог-файл; в консоль traceback не выводится."""
    logger.error(message, extra={FILE_ONLY: True})


def log_exception_once(target: logging.Logger, message: str, exc: BaseException) -> None:
    """Записать ERROR с traceback исключения; повторный вызов для того же объекта ничего не пишет.

    Traceback видит только файл (консольный форматтер его подавляет). Флаг «уже записано» нужен, чтобы
    ошибка, пройдя оркестратор и границу оболочки, не получила два traceback.
    """
    if exc.__dict__.get(_LOGGED_FLAG):
        return
    exc.__dict__[_LOGGED_FLAG] = True
    target.error(message, exc_info=exc)
