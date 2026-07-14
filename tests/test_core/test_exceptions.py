"""tests for core exceptions"""

from unittest.mock import patch

import pytest

from core.exceptions import CoreExceptionError, SupplierNotHavePricesError, make_raise

_TO_LOG = "to_log"


class _CustomError(CoreExceptionError):
    """ошибка с сообщением по умолчанию"""

    __MESSAGE__ = "default msg"  # noqa: WPS115


def test_core_exception_logs_message():
    """CoreExceptionError пишет в лог и сохраняет сообщение"""
    with patch.object(CoreExceptionError, _TO_LOG) as mock_log:
        exc = CoreExceptionError("ошибка")
        assert str(exc) == "ошибка"
        mock_log.assert_called_once_with("ошибка")


def test_core_exception_default_message():
    """без аргумента берётся __MESSAGE__"""
    with patch.object(CoreExceptionError, _TO_LOG):
        assert str(_CustomError()) == "default msg"


def test_make_raise():
    """make_raise поднимает CoreExceptionError"""
    with patch.object(CoreExceptionError, _TO_LOG):
        with pytest.raises(CoreExceptionError, match="fail"):
            make_raise("fail")


def test_supplier_error_type():
    """SupplierNotHavePricesError наследует CoreExceptionError"""
    with patch.object(CoreExceptionError, _TO_LOG):
        assert isinstance(SupplierNotHavePricesError("empty"), CoreExceptionError)


def test_to_log_calls_err_msg():
    """to_log формирует stack-trace и вызывает err_msg"""
    with patch("core.exceptions.err_msg") as mock_err:
        CoreExceptionError.to_log("trace-me")
        mock_err.assert_called_once()
        assert "trace-me" in mock_err.call_args.args[0]
