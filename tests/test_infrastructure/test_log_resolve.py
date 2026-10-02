"""tests for log level labels"""

import logging

from infrastructure.logging.log_resolve import get_log_level_text

_UNKNOWN_LEVEL = 999


def test_get_log_level_text_known() -> None:
    """известные уровни"""
    assert get_log_level_text(logging.ERROR) == 'ERROR'
    assert get_log_level_text(logging.WARNING) == 'WARNING'


def test_get_log_level_text_fallback() -> None:
    """неизвестный уровень → INFO"""
    assert get_log_level_text(_UNKNOWN_LEVEL) == 'INFO'
