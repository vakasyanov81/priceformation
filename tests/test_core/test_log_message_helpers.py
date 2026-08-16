"""tests for log_message helpers beyond print_log"""

import logging
from unittest.mock import patch

from cfg import init_cfg
from core.log_message import err_msg, log_msg, warn_msg
from core.log_paths import LogPaths, configure_log_paths, get_log_paths
from core.log_resolve import (
    get_log_level_text,
    resolve_log_method,
    resolve_log_path,
)

_UNKNOWN_LEVEL = 999
_UNKNOWN_METHOD_LEVEL = 12345


def test_get_log_level_text_known() -> None:
    """известные уровни"""
    assert get_log_level_text(logging.ERROR) == "ERROR"
    assert get_log_level_text(logging.WARNING) == "WARNING"


def test_get_log_level_text_fallback() -> None:
    """неизвестный уровень → INFO"""
    assert get_log_level_text(_UNKNOWN_LEVEL) == "INFO"


def test_resolve_log_path_by_level() -> None:
    """ERROR идёт в err-лог, остальное — в обычный"""
    configure_log_paths(
        LogPaths(
            folder="/var/log/priceformation",
            log_file="/var/log/priceformation/info.log",
            err_file="/var/log/priceformation/err.log",
        )
    )
    assert resolve_log_path(logging.ERROR) == "/var/log/priceformation/err.log"
    assert resolve_log_path(logging.INFO) == "/var/log/priceformation/info.log"


def test_init_cfg_configures_log_paths() -> None:
    """init_cfg передаёт пути логов в core, без импорта cfg из core."""
    compiler = init_cfg()
    paths = get_log_paths()
    assert paths.folder == compiler.main.log_folder_path
    assert paths.log_file == compiler.main.current_log_file_path
    assert paths.err_file == compiler.main.current_err_log_file_path


def test_resolve_log_method_mapping() -> None:
    """маппинг методов logging по уровню"""
    assert resolve_log_method(logging.ERROR) is logging.error
    assert resolve_log_method(logging.WARNING) is logging.warning
    assert resolve_log_method(logging.INFO) is logging.info
    assert resolve_log_method(_UNKNOWN_METHOD_LEVEL) is logging.info


def test_warn_msg_delegates() -> None:
    """warn_msg вызывает log_msg с WARNING"""
    with patch("core.log_message.log_msg", return_value="w") as mock_log:
        assert warn_msg("attention", need_print_log=True) == "w"
        mock_log.assert_called_once_with(
            "attention",
            level=logging.WARNING,
            need_print_log=True,
        )


def test_err_msg_delegates() -> None:
    """err_msg вызывает log_msg с ERROR"""
    with patch("core.log_message.log_msg", return_value="e") as mock_log:
        assert err_msg("bad", need_print_log=False) == "e"
        mock_log.assert_called_once_with("bad", level=logging.ERROR, need_print_log=False)


def test_log_msg_error_writes_file() -> None:
    """ERROR-уровень пишет в файл и возвращает сообщение со временем"""
    with (
        patch("core.log_message.log_to_file") as mock_file,
        patch("core.log_message.print_log") as mock_print,
    ):
        message = log_msg("boom", level=logging.ERROR, need_print_log=True)
        mock_file.assert_called_once()
        mock_print.assert_called_once()
        assert "boom" in message
