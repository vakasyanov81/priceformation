"""tests for the infrastructure side of the exception log sink"""

from unittest.mock import patch

import pytest

from infrastructure.logging.exception_logging import write_exception_log

_LOG_UNAVAILABLE = 'Log paths are not configured'


def test_write_exception_log_to_file() -> None:
    """сообщение уходит в лог-файл, не в консоль"""
    with patch('infrastructure.logging.exception_logging.err_msg') as mock_err:
        write_exception_log('trace-me')

    mock_err.assert_called_once_with('trace-me', need_print_log=False)


@pytest.mark.parametrize('error', [RuntimeError(_LOG_UNAVAILABLE), PermissionError('denied')])
def test_write_exception_log_fallback(error: Exception) -> None:
    """недоступный лог-файл не пробрасывает ошибку наружу"""
    with (
        patch('infrastructure.logging.exception_logging.err_msg', side_effect=error),
        patch('infrastructure.logging.exception_logging.logging.error') as mock_err,
    ):
        write_exception_log('trace-me')

    mock_err.assert_called_once_with('trace-me')
