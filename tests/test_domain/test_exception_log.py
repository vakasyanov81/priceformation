"""tests for the domain exception log sink holder"""

from collections.abc import Iterator

import pytest

from domain.exception_log import _CurrentExceptionLog, log_exception, set_exception_log_sink


@pytest.fixture
def _sink_restored() -> Iterator[None]:
    previous = _CurrentExceptionLog.sink
    yield
    _CurrentExceptionLog.sink = previous


def test_log_exception_passes_to_sink(_sink_restored: None) -> None:
    """назначенный приёмник получает сообщение"""
    received: list[str] = []
    set_exception_log_sink(received.append)

    log_exception('boom')

    assert received == ['boom']


def test_log_exception_without_sink(_sink_restored: None) -> None:
    """без приёмника сообщение просто не пишется"""
    set_exception_log_sink(None)

    log_exception('boom')


def test_sink_can_be_replaced(_sink_restored: None) -> None:
    """последний назначенный приёмник выигрывает"""
    first: list[str] = []
    second: list[str] = []
    set_exception_log_sink(first.append)
    set_exception_log_sink(second.append)

    log_exception('boom')

    assert not first
    assert second == ['boom']
