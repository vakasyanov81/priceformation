"""Настройка логирования: корневой логгер, консоль и файлы логов.

Модули логируют через ``logging.getLogger(__name__)``, а обработчики и их уровни
настраивает ``setup_logging``: консоль всегда, файлы — когда известны пути.
"""

import logging
from collections.abc import Sequence

from colorama import init

from infrastructure.logging.console import ConsoleHandler
from infrastructure.logging.file_logging import build_file_handlers, prepare_log_folder
from infrastructure.logging.log_paths import LogPaths

init()

__SETUP_MARK__ = 'priceformation_setup_handler'


def setup_logging(paths: LogPaths | None = None, level: int = logging.INFO) -> None:
    """Настроить корневой логгер: консоль и, при известных путях, файлы логов.

    Повторный вызов снимает ранее добавленные обработчики, чужие не трогает.
    Недоступная папка логов не мешает: остаётся только консоль.
    """
    root = logging.getLogger()
    _remove_setup_handlers(root)
    root.setLevel(level)
    _attach_handlers(root, [ConsoleHandler()])
    if paths is not None and prepare_log_folder(paths.folder):
        _attach_handlers(root, build_file_handlers(paths))


def _attach_handlers(root: logging.Logger, handlers: Sequence[logging.Handler]) -> None:
    """Пометить обработчики меткой настройки и добавить их к корневому логгеру."""
    for log_handler in handlers:
        setattr(log_handler, __SETUP_MARK__, True)
        root.addHandler(log_handler)


def _remove_setup_handlers(root: logging.Logger) -> None:
    """Снять и закрыть обработчики прошлой настройки, не трогая чужие."""
    for log_handler in list(root.handlers):
        if getattr(log_handler, __SETUP_MARK__, False):
            root.removeHandler(log_handler)
            log_handler.close()


__ALL__ = ['setup_logging']
