"""tests for the root logger setup"""

import logging
from pathlib import Path

import pytest

from infrastructure.logging.console import FILE_ONLY, ConsoleHandler
from infrastructure.logging.json_mode import json_mode_active, set_json_mode
from infrastructure.logging.log_paths import LogPaths
from infrastructure.logging.log_setup import setup_logging

_NOISY_LOGGER = 'tests.noisy'


def test_setup_logging_console_by_default(capsys: pytest.CaptureFixture[str]) -> None:
    """без путей настраивается только консоль"""
    setup_logging()

    logging.getLogger(_NOISY_LOGGER).info('bare message')

    assert capsys.readouterr().out == 'bare message\n'


def test_setup_logging_levels_on_console(capsys: pytest.CaptureFixture[str]) -> None:
    """уровень выше INFO печатается с префиксом"""
    setup_logging()
    noisy = logging.getLogger(_NOISY_LOGGER)

    noisy.warning('careful')
    noisy.error('boom')

    out = capsys.readouterr().out
    assert '[WARNING]: careful\n' in out
    assert '[ERROR]: boom\n' in out


def test_setup_logging_respects_level(capsys: pytest.CaptureFixture[str]) -> None:
    """уровень из setup_logging режет всё ниже"""
    setup_logging(level=logging.WARNING)
    noisy = logging.getLogger(_NOISY_LOGGER)

    noisy.info('hidden')
    noisy.warning('shown')

    out = capsys.readouterr().out
    assert 'hidden' not in out
    assert '[WARNING]: shown\n' in out


def test_setup_logging_keeps_foreign_handlers() -> None:
    """повторная настройка снимает только свои обработчики"""
    root = logging.getLogger()
    foreign = logging.NullHandler()
    root.addHandler(foreign)

    setup_logging()
    setup_logging()

    console_handlers = [log_handler for log_handler in root.handlers if isinstance(log_handler, ConsoleHandler)]
    assert foreign in root.handlers
    assert len(console_handlers) == 1


def test_setup_logging_writes_log_and_error_files(tmp_path: Path) -> None:
    """сообщения идут в файлы логов, ошибки — ещё и в отдельный файл"""
    paths = LogPaths.for_folder(str(tmp_path))
    setup_logging(paths)
    noisy = logging.getLogger(_NOISY_LOGGER)

    noisy.info('в общий лог')
    noisy.error('в оба лога')

    log_text = Path(paths.log_file).read_text(encoding='utf-8')
    err_text = Path(paths.err_file).read_text(encoding='utf-8')
    assert '[INFO] tests.noisy: в общий лог' in log_text
    assert 'в оба лога' in log_text
    assert 'в общий лог' not in err_text
    assert 'в оба лога' in err_text


def test_setup_logging_unavailable_folder(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """недоступная папка логов не мешает: остаётся только консоль"""
    blocker = tmp_path / 'blocker'
    blocker.write_text('not a folder', encoding='utf-8')

    setup_logging(LogPaths.for_folder(str(blocker)))
    logging.getLogger(_NOISY_LOGGER).info('only console')

    assert capsys.readouterr().out == 'only console\n'


def test_json_mode_silences_console(capsys: pytest.CaptureFixture[str]) -> None:
    """JSON-режим гасит консольный обработчик, а не само логирование"""
    setup_logging()
    set_json_mode(True)
    assert json_mode_active()

    logging.getLogger(_NOISY_LOGGER).info('скрыто')
    assert capsys.readouterr().out == ''

    set_json_mode(False)
    assert not json_mode_active()
    logging.getLogger(_NOISY_LOGGER).info('видно')
    assert capsys.readouterr().out == 'видно\n'


def test_file_only_record_stays_out_of_console(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """запись с extra[FILE_ONLY] уходит только в файл"""
    paths = LogPaths.for_folder(str(tmp_path))
    setup_logging(paths)

    logging.getLogger(_NOISY_LOGGER).error('только файл', extra={FILE_ONLY: True})

    assert capsys.readouterr().out == ''
    assert 'только файл' in Path(paths.err_file).read_text(encoding='utf-8')
