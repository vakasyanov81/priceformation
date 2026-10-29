"""Консольный обработчик логов: цветной вывод, который уважает JSON-режим."""

import copy
import logging
import sys

from termcolor import colored

from infrastructure.logging.json_mode import json_mode_active
from infrastructure.logging.log_resolve import get_level_color, get_log_level_text

__CONSOLE_FORMAT__ = '%(message)s'
FILE_ONLY = 'file_only'


class JsonModeFilter(logging.Filter):
    """В JSON-режиме консоль не пишет ничего: stdout остаётся под JSON-ответ."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Пропустить запись, если JSON-режим выключен."""
        return not json_mode_active()


class FileOnlyFilter(logging.Filter):
    """Записи с ``extra={FILE_ONLY: True}`` идут только в файл, не в консоль."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Пропустить запись, если она не помечена как только для файла."""
        return not getattr(record, FILE_ONLY, False)


def _without_traceback(record: logging.LogRecord) -> logging.LogRecord:
    """Копия записи без traceback: ``exc_text`` кэшируется на записи и иначе просочился бы из файлового handler."""
    plain = copy.copy(record)
    plain.exc_info = None
    plain.exc_text = None
    return plain


class ConsoleFormatter(logging.Formatter):
    """Консольный вид сообщения: INFO — голый текст, прочие уровни с префиксом и цветом; traceback не печатает."""

    def format(self, record: logging.LogRecord) -> str:
        """Текст записи с префиксом уровня и подсветкой."""
        level_text = get_log_level_text(record.levelno)
        message = super().format(_without_traceback(record))
        formatted = message if record.levelno == logging.INFO else f'[{level_text}]: {message}'
        return colored(formatted, get_level_color(level_text))


class ConsoleHandler(logging.Handler):
    """Пишет в текущий ``sys.stdout``: перенаправление и capture не ломают вывод."""

    def __init__(self) -> None:
        super().__init__()
        self.addFilter(JsonModeFilter())
        self.addFilter(FileOnlyFilter())
        self.setFormatter(ConsoleFormatter(__CONSOLE_FORMAT__))

    def emit(self, record: logging.LogRecord) -> None:
        """Напечатать запись в актуальный ``sys.stdout``."""
        try:
            sys.stdout.write(f'{self.format(record)}\n')
        except Exception:  # логирование не должно ронять приложение
            self.handleError(record)


__ALL__ = ['FILE_ONLY', 'ConsoleHandler', 'FileOnlyFilter', 'JsonModeFilter']
