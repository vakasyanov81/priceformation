"""tests for the infrastructure side of the exception log sink"""

import logging
from pathlib import Path

import pytest

from infrastructure.logging.exception_logging import write_exception_log
from infrastructure.logging.log_paths import LogPaths
from infrastructure.logging.log_setup import setup_logging

_TRACE = 'trace-me'


def test_write_exception_log_to_file(tmp_path: Path) -> None:
    """сообщение уходит в лог-файл"""
    paths = LogPaths.for_folder(str(tmp_path))
    setup_logging(paths)

    write_exception_log(_TRACE)

    assert _TRACE in Path(paths.err_file).read_text(encoding='utf-8')


def test_write_exception_log_stays_out_of_console(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """traceback домена — только файл, консоль пользователя не засоряется"""
    setup_logging(LogPaths.for_folder(str(tmp_path)))

    write_exception_log(_TRACE)

    assert capsys.readouterr().out == ''


def test_write_exception_log_without_setup(caplog: pytest.LogCaptureFixture) -> None:
    """без настроенного логгера вызов не падает и остаётся записью ERROR"""
    caplog.set_level(logging.ERROR)

    write_exception_log(_TRACE)

    assert _TRACE in caplog.text
