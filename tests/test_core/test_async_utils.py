"""tests for try_call helper"""

from unittest.mock import MagicMock, patch

import pytest

from core.async_utils import try_call
from core.exceptions import SupplierNotHavePricesError


def test_try_call_success():
    """успешный вызов метода с kwargs"""
    method = MagicMock()
    try_call(method, a=1, b=2)
    method.assert_called_once_with(a=1, b=2)


def test_try_call_supplier_error_exits():
    """SupplierNotHavePricesError логируется и завершает процесс"""
    with patch.object(SupplierNotHavePricesError, "to_log"):
        method = MagicMock(side_effect=SupplierNotHavePricesError("нет прайса"))

    with (
        patch("core.async_utils.print_log") as mock_log,
        patch("core.async_utils.sys.exit") as mock_exit,
    ):
        try_call(method)
        mock_log.assert_called_once()
        mock_exit.assert_called_once_with(1)


def test_try_call_keyboard_interrupt():
    """KeyboardInterrupt завершает процесс с кодом 0"""
    method = MagicMock(side_effect=KeyboardInterrupt)

    with patch("core.async_utils.sys.exit") as mock_exit:
        try_call(method)
        mock_exit.assert_called_once_with(0)


def test_try_call_other_exception():
    """прочие исключения пробрасываются наверх"""
    method = MagicMock(side_effect=ValueError("boom"))

    with pytest.raises(ValueError, match="boom"):
        try_call(method)
