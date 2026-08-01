"""
test init_log
"""

from typing import Any
from unittest.mock import patch

from core.wrappers import logging


@logging(label="test_logging")
def logging_function(param1: int, param2: int, **_dict: Any) -> int:
    """decorated function for logging wrapper test"""
    return param1 + param2


def test_logging() -> None:
    """logging wrapper emits call/result messages"""
    param1, param2 = 10, 20
    expected_result = param1 + param2
    with patch("core.wrappers.log_msg") as mock_log_msg:
        logging_function(param1, param2, other_param="some text")
    assert mock_log_msg.call_count == 3
    first_msg = str(mock_log_msg.call_args_list[0].args[0])
    second_msg = str(mock_log_msg.call_args_list[1].args[0])
    assert "Calling method" in first_msg
    assert f"Params: ({param1}, {param2})" in first_msg
    assert "{'other_param': 'some text'}" in first_msg
    assert "Result" in second_msg
    assert f'logging_function": {expected_result}' in second_msg


def test_logging_when_wrong_argument() -> None:
    """test logging call function with wrong argument"""

    with patch("core.wrappers.log_msg") as mock_log_msg:
        try:
            logging_function()
        except TypeError:
            pass

    assert mock_log_msg.call_count == 4
    assert "Calling method" in str(mock_log_msg.call_args_list[0].args[0])
    assert "logging_function" in str(mock_log_msg.call_args_list[0].args[0])
    assert "Label test_logging" in str(mock_log_msg.call_args_list[0].args[0])

    assert "Runtime error" in str(mock_log_msg.call_args_list[1].args[0])
    assert "missing 2 required positional arguments" in str(mock_log_msg.call_args_list[1].args[0])

    assert "Result" in str(mock_log_msg.call_args_list[2].args[0])
    assert ": None" in str(mock_log_msg.call_args_list[2].args[0])

    assert "End of call to method" in str(mock_log_msg.call_args_list[3].args[0])
    assert "[exec_period]" in str(mock_log_msg.call_args_list[3].args[0])
