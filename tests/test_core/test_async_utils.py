"""tests for try_call helper"""

import logging
from unittest.mock import MagicMock, patch

import pytest

from core.async_utils import try_call
from core.exceptions import CoreExceptionError, SupplierNotHavePricesError


def test_try_call_success() -> None:
    """успешный вызов метода с kwargs"""
    method = MagicMock()
    try_call(method, a=1, b=2)
    method.assert_called_once_with(a=1, b=2)


def test_try_call_supplier_error_exits() -> None:
    """SupplierNotHavePricesError логируется и завершает процесс"""
    with patch.object(SupplierNotHavePricesError, "to_log"):
        method = MagicMock(side_effect=SupplierNotHavePricesError("нет прайса"))

    with (
        patch("core.async_utils.print_log") as mock_log,
        patch("core.async_utils.sys.exit") as mock_exit,
    ):
        try_call(method)
        mock_log.assert_called_once()
        assert mock_log.call_args.kwargs["level"] == logging.WARNING
        mock_exit.assert_called_once_with(1)


def test_try_call_keyboard_interrupt() -> None:
    """KeyboardInterrupt завершает процесс с кодом 0"""
    method = MagicMock(side_effect=KeyboardInterrupt)

    with patch("core.async_utils.sys.exit") as mock_exit:
        try_call(method)
        mock_exit.assert_called_once_with(0)


def test_try_call_core_error() -> None:
    """CoreExceptionError печатается в консоль, процесс не завершается"""
    with patch.object(CoreExceptionError, "to_log"):
        method = MagicMock(side_effect=CoreExceptionError("понятная ошибка"))

    with (
        patch("core.async_utils.print_log") as mock_log,
        patch("core.async_utils.sys.exit") as mock_exit,
    ):
        try_call(method)
        mock_log.assert_called_once()
        assert "понятная ошибка" in mock_log.call_args.args[0]
        assert mock_log.call_args.kwargs["level"] == logging.ERROR
        mock_exit.assert_not_called()


def test_try_call_other_exception() -> None:
    """прочие исключения пробрасываются наверх"""
    method = MagicMock(side_effect=ValueError("boom"))

    with pytest.raises(ValueError, match="boom"):
        try_call(method)
