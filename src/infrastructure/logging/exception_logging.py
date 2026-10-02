"""Запись сообщений об исключениях домена в лог инфраструктуры."""

import logging

from infrastructure.logging.log_message import err_msg


def write_exception_log(message: str) -> None:
    """Писать в лог-файл; если он недоступен — в logging модуль."""
    try:
        err_msg(message, need_print_log=False)
    except RuntimeError, OSError:
        logging.error(message)
