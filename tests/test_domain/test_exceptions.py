"""tests for domain exceptions"""

from unittest.mock import patch

import pytest

from domain.exceptions import (
    CoreExceptionError,
    SupplierNotHavePricesError,
    make_raise,
)

_TO_LOG = 'to_log'
_STACK_LIMIT = 10


class _CustomError(CoreExceptionError):
    """ошибка с сообщением по умолчанию"""

    __MESSAGE__ = 'default msg'  # noqa: WPS115


def test_core_exception_logs_message() -> None:
    """CoreExceptionError пишет в лог и сохраняет сообщение"""
    with patch.object(CoreExceptionError, _TO_LOG) as mock_log:
        exc = CoreExceptionError('ошибка')
        assert str(exc) == 'ошибка'
        mock_log.assert_called_once_with('ошибка')


def test_core_exception_logs_detail() -> None:
    """в лог уходит detail, в str — пользовательское сообщение"""
    with patch.object(CoreExceptionError, _TO_LOG) as mock_log:
        exc = CoreExceptionError('понятно', detail='stack and cause')
        assert str(exc) == 'понятно'
        mock_log.assert_called_once_with('stack and cause')


def test_core_exception_default_message() -> None:
    """без аргумента берётся __MESSAGE__"""
    with patch.object(CoreExceptionError, _TO_LOG):
        assert str(_CustomError()) == 'default msg'


def test_make_raise() -> None:
    """make_raise поднимает CoreExceptionError"""
    with patch.object(CoreExceptionError, _TO_LOG), pytest.raises(CoreExceptionError, match='fail'):
        make_raise('fail')


def test_supplier_error_type() -> None:
    """SupplierNotHavePricesError наследует CoreExceptionError"""
    with patch.object(CoreExceptionError, _TO_LOG):
        assert isinstance(SupplierNotHavePricesError('empty'), CoreExceptionError)


def test_to_log_passes_message_with_stack_to_sink() -> None:
    """to_log отдаёт приёмнику сообщение и стек вызовов"""
    with patch('domain.exceptions.log_exception') as mock_log:
        CoreExceptionError.to_log('trace-me')

    mock_log.assert_called_once()
    assert 'trace-me' in mock_log.call_args.args[0]
    assert 'test_to_log_passes_message_with_stack_to_sink' in mock_log.call_args.args[0]


def test_to_log_without_message() -> None:
    """без сообщения приёмник всё равно получает стек"""
    with patch('domain.exceptions.log_exception') as mock_log:
        CoreExceptionError.to_log(None)

    mock_log.assert_called_once()
    assert 'None' in mock_log.call_args.args[0]


def test_to_log_limits_stack_depth(monkeypatch: pytest.MonkeyPatch) -> None:
    """to_log ограничивает стек константой глубины, а не всем стеком."""
    recorded: dict[str, int | None] = {}

    def _extract_stack(*, limit: int | None = None) -> list[object]:
        recorded['limit'] = limit
        return []

    monkeypatch.setattr('domain.exceptions.traceback.extract_stack', _extract_stack)
    with patch('domain.exceptions.log_exception'):
        CoreExceptionError.to_log('trace-me')
    assert recorded['limit'] == _STACK_LIMIT
