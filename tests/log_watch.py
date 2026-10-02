"""Типы и сбор записей логгера для тестов (используется фикстурой watch_logger)."""

from collections.abc import Callable

import pytest

LogEntry = tuple[int, str]
LoggerWatch = Callable[[], list[LogEntry]]
LoggerWatcher = Callable[[str, int], LoggerWatch]


def records_of(caplog: pytest.LogCaptureFixture, logger_name: str) -> list[LogEntry]:
    """Записи указанного логгера как пары (уровень, текст)."""
    own = [record for record in caplog.records if record.name == logger_name]
    return [(record.levelno, record.getMessage()) for record in own]


def texts_at(entries: list[LogEntry], level: int) -> list[str]:
    """Тексты записей одного уровня из собранных пар."""
    return [message for entry_level, message in entries if entry_level == level]
