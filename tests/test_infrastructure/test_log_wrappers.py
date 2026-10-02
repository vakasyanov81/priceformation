"""tests for the call logging decorator"""

from contextlib import suppress
from logging import DEBUG, WARNING
from typing import Any

from log_watch import LoggerWatcher

from infrastructure.logging.wrappers import logging

_WRAPPER_LOGGER = 'infrastructure.logging.wrappers'


@logging(label='test_logging')
def logging_function(param1: int, param2: int, **_dict: Any) -> int:
    """decorated function for logging wrapper test"""
    return param1 + param2


def test_logging(watch_logger: LoggerWatcher) -> None:
    """logging wrapper emits call/result messages"""
    param1, param2 = 10, 20
    expected_result = param1 + param2
    entries = watch_logger(_WRAPPER_LOGGER, DEBUG)

    logging_function(param1, param2, other_param='some text')

    messages = [message for _level, message in entries()]
    assert len(messages) == 3
    first_msg, second_msg, third_msg = messages
    assert 'Calling method' in first_msg
    assert f'Params: ({param1}, {param2})' in first_msg
    assert "{'other_param': 'some text'}" in first_msg
    assert 'Label test_logging' in first_msg
    assert 'Result' in second_msg
    assert f'logging_function": {expected_result}' in second_msg
    assert 'End of call to method' in third_msg
    assert '[exec_period]' in third_msg


def test_logging_messages_are_debug(watch_logger: LoggerWatcher) -> None:
    """детали вызова идут на уровне DEBUG: консоль и INFO-лог их не видят"""
    entries = watch_logger(_WRAPPER_LOGGER, DEBUG)

    logging_function(1, 2)

    levels = [level for level, _message in entries()]
    assert levels
    assert set(levels) == {DEBUG}


def test_logging_when_wrong_argument(watch_logger: LoggerWatcher) -> None:
    """test logging call function with wrong argument"""
    entries = watch_logger(_WRAPPER_LOGGER, DEBUG)

    with suppress(TypeError):
        logging_function()

    messages = [message for level, message in entries() if level == DEBUG]
    assert len(messages) == 3
    first_msg, second_msg, third_msg = messages
    assert 'Calling method' in first_msg
    assert 'logging_function' in first_msg
    assert 'Label test_logging' in first_msg

    assert 'Result' in second_msg
    assert ': None' in second_msg

    assert 'End of call to method' in third_msg
    assert '[exec_period]' in third_msg


def test_logging_when_wrong_argument_logs_trace(
    watch_logger: LoggerWatcher,
) -> None:
    """ошибка вызова логируется как WARNING с traceback"""
    entries = watch_logger(_WRAPPER_LOGGER, DEBUG)

    with suppress(TypeError):
        logging_function()

    warnings = [message for level, message in entries() if level == WARNING]
    assert len(warnings) == 1
    assert 'Runtime error' in warnings[0]
    assert 'missing 2 required positional arguments' in warnings[0]
