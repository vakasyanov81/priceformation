"""tests for log_paths injection"""

from collections.abc import Iterator

import pytest

from core.log_paths import (
    LogPaths,
    _CurrentLogPaths,
    configure_log_paths,
    get_log_paths,
)

_FOLDER = "/var/log"
_LOG_FILE = "/var/log/log_2026-01-01.log"
_ERR_FILE = "/var/log/error_2026-01-01.log"


@pytest.fixture
def _restore_log_paths() -> Iterator[None]:
    previous = _CurrentLogPaths.configured
    yield
    _CurrentLogPaths.configured = previous


def test_configure_and_get_log_paths(_restore_log_paths: None) -> None:
    """configure_log_paths сохраняет пути для get_log_paths."""
    configure_log_paths(
        LogPaths(folder=_FOLDER, log_file=_LOG_FILE, err_file=_ERR_FILE),
    )
    paths = get_log_paths()
    assert paths.folder == _FOLDER
    assert paths.log_file == _LOG_FILE
    assert paths.err_file == _ERR_FILE


def test_get_log_paths_requires_configure(_restore_log_paths: None) -> None:
    """без configure_log_paths — явная ошибка."""
    _CurrentLogPaths.configured = None
    with pytest.raises(RuntimeError, match="Log paths are not configured"):
        get_log_paths()


def test_log_paths_not_configured_error_message() -> None:
    """LogPathsNotConfiguredError содержит стандартное сообщение."""
    from core.log_paths import LogPathsNotConfiguredError

    error = LogPathsNotConfiguredError()
    assert str(error) == "Log paths are not configured"
