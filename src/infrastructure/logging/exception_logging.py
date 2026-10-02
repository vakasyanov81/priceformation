"""Запись сообщений об исключениях домена в лог инфраструктуры."""

import logging

from infrastructure.logging.console import FILE_ONLY

logger = logging.getLogger(__name__)


def write_exception_log(message: str) -> None:
    """Писать в лог-файл; в консоль traceback не выводится."""
    logger.error(message, extra={FILE_ONLY: True})
