"""tests for the console log handler and its filters"""

import io
import logging
import sys
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.logging.console import FILE_ONLY, ConsoleFormatter, ConsoleHandler


def _record(message: str = 'message', level: int = logging.INFO, file_only: bool = False) -> logging.LogRecord:
    """Запись логгера для проверки формата и обработки."""
    record = logging.LogRecord('tests.console', level, __file__, 1, message, None, None)
    if file_only:
        setattr(record, FILE_ONLY, True)
    return record


def test_console_formatter_plain_info() -> None:
    """INFO печатается без префикса"""
    assert ConsoleFormatter().format(_record('bare')) == 'bare'


def test_console_formatter_prefixes_other_levels() -> None:
    """остальные уровни помечаются префиксом"""
    formatted = ConsoleFormatter().format(_record('careful', logging.WARNING))

    assert '[WARNING]: careful' in formatted


def test_console_handler_writes_to_current_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """обработчик берёт sys.stdout в момент записи"""
    console = ConsoleHandler()
    console.emit(_record('to stdout'))

    assert capsys.readouterr().out == 'to stdout\n'


def test_console_handler_follows_redirected_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """после подмены sys.stdout вывод идёт в новое место"""
    stream = io.StringIO()
    console = ConsoleHandler()

    with patch.object(sys, 'stdout', stream):
        console.emit(_record('redirected'))

    assert stream.getvalue() == 'redirected\n'
    assert capsys.readouterr().out == ''


def test_console_handler_survives_broken_stream() -> None:
    """падающий stdout не роняет приложение"""
    console = ConsoleHandler()
    record = _record()
    broken_stream = MagicMock()
    broken_stream.write.side_effect = OSError('stream closed')

    with (
        patch.object(sys, 'stdout', broken_stream),
        patch.object(console, 'handleError') as mock_handle_error,
    ):
        console.emit(record)

    mock_handle_error.assert_called_once_with(record)


def test_console_handler_skips_file_only_records(capsys: pytest.CaptureFixture[str]) -> None:
    """запись с extra[FILE_ONLY] не доходит до консоли"""
    console = ConsoleHandler()
    console.handle(_record('только файл', logging.ERROR, file_only=True))

    assert capsys.readouterr().out == ''
