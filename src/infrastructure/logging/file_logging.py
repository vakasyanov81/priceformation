"""Файловые обработчики логов: общий журнал и отдельный журнал ошибок."""

import logging
from pathlib import Path

from infrastructure.logging.log_paths import LogPaths

__FILE_FORMAT__ = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
__FILE_ENCODING__ = 'utf-8'


def build_file_handlers(paths: LogPaths) -> list[logging.FileHandler]:
    """Обработчики файлов логов: общий для INFO+ и отдельный для ошибок.

    Файлы открываются с задержкой, поэтому недоступный лог не ломает запуск.
    """
    return [
        _build_file_handler(paths.log_file, logging.INFO),
        _build_file_handler(paths.err_file, logging.ERROR),
    ]


def prepare_log_folder(log_folder: str) -> bool:
    """Создать папку логов; недоступная папка — False, логи остаются в консоли."""
    try:
        Path(log_folder).mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    return True


def _build_file_handler(path: str, level: int) -> logging.FileHandler:
    """Файловый обработчик с указанным уровнем и общим форматом записи."""
    log_handler = logging.FileHandler(path, encoding=__FILE_ENCODING__, delay=True)
    log_handler.setLevel(level)
    log_handler.setFormatter(logging.Formatter(__FILE_FORMAT__))
    return log_handler
