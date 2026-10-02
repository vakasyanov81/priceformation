"""tests for the log file handlers and the log folder"""

import logging
from pathlib import Path
from unittest.mock import patch

from infrastructure.logging.file_logging import build_file_handlers, prepare_log_folder
from infrastructure.logging.log_paths import LogPaths


def test_prepare_log_folder_creates_parents() -> None:
    """папка логов создаётся вместе с недостающими родителями"""
    with patch.object(Path, 'mkdir') as mock_mkdir:
        assert prepare_log_folder('/var/log/priceformation/nested')

    assert mock_mkdir.call_args.kwargs == {'parents': True, 'exist_ok': True}


def test_prepare_log_folder_keeps_existing_folder(tmp_path: Path) -> None:
    """существующая папка подходит, повторный запуск не мешает"""
    assert prepare_log_folder(str(tmp_path))
    assert prepare_log_folder(str(tmp_path))


def test_prepare_log_folder_reports_unavailable_folder(tmp_path: Path) -> None:
    """недоступная папка — False, вызывающий код остаётся только с консолью"""
    blocker = tmp_path / 'blocker'
    blocker.write_text('not a folder', encoding='utf-8')

    assert not prepare_log_folder(str(blocker))


def test_build_file_handlers_levels_and_paths(tmp_path: Path) -> None:
    """строятся общий файл для INFO+ и отдельный для ошибок"""
    paths = LogPaths.for_folder(str(tmp_path))
    general, error_only = build_file_handlers(paths)

    assert general.baseFilename == paths.log_file
    assert general.level == logging.INFO
    assert error_only.baseFilename == paths.err_file
    assert error_only.level == logging.ERROR
    general.close()
    error_only.close()


def test_build_file_handlers_formats_record(tmp_path: Path) -> None:
    """формат записи в файле: время, уровень, логгер и сообщение"""
    paths = LogPaths.for_folder(str(tmp_path))
    general, error_only = build_file_handlers(paths)

    record = logging.LogRecord('tests.file', logging.INFO, __file__, 1, 'в файл', None, None)
    general.emit(record)
    general.close()
    error_only.close()

    assert '[INFO] tests.file: в файл' in Path(paths.log_file).read_text(encoding='utf-8')
