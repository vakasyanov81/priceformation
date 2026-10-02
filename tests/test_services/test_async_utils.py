"""tests for try_call helper"""

from logging import ERROR, WARNING
from unittest.mock import MagicMock, patch

import pytest
from log_watch import LoggerWatcher

from domain.exceptions import CoreExceptionError, SupplierNotHavePricesError
from services.async_utils import try_call

_ASYNC_LOGGER = 'services.async_utils'


def test_try_call_success() -> None:
    """успешный вызов метода с kwargs"""
    method = MagicMock()
    try_call(method, a=1, b=2)
    method.assert_called_once_with(a=1, b=2)


def test_try_call_supplier_error_exits(watch_logger: LoggerWatcher) -> None:
    """SupplierNotHavePricesError логируется и завершает процесс"""
    entries = watch_logger(_ASYNC_LOGGER)
    with patch.object(SupplierNotHavePricesError, 'to_log'):
        method = MagicMock(side_effect=SupplierNotHavePricesError('нет прайса'))

    with patch('services.async_utils.sys.exit') as mock_exit:
        try_call(method)

    assert entries() == [(WARNING, 'нет прайса')]
    mock_exit.assert_called_once_with(1)


def test_try_call_keyboard_interrupt() -> None:
    """KeyboardInterrupt завершает процесс с кодом 0"""
    method = MagicMock(side_effect=KeyboardInterrupt)

    with patch('services.async_utils.sys.exit') as mock_exit:
        try_call(method)
    mock_exit.assert_called_once_with(0)


def test_try_call_core_error(watch_logger: LoggerWatcher) -> None:
    """CoreExceptionError печатается в консоль, процесс не завершается"""
    entries = watch_logger(_ASYNC_LOGGER)
    with patch.object(CoreExceptionError, 'to_log'):
        method = MagicMock(side_effect=CoreExceptionError('понятная ошибка'))

    with patch('services.async_utils.sys.exit') as mock_exit:
        try_call(method)

    assert entries() == [(ERROR, 'понятная ошибка')]
    mock_exit.assert_not_called()


def test_try_call_other_exception() -> None:
    """прочие исключения пробрасываются наверх"""
    method = MagicMock(side_effect=ValueError('boom'))

    with pytest.raises(ValueError, match='boom'):
        try_call(method)
