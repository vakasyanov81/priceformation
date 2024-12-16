# -*- coding: utf-8 -*-
"""
test init_log
"""
__author__ = "Kasyanov V.A."

from unittest.mock import patch

from src.core.wrappers import logging


@logging(label="test_logging")
def logging_function(param1: int, param2: int, **_dict):
    return param1 + param2


def test_logging():
    param1, param2 = 10, 20
    with patch("src.core.wrappers.log_msg") as _mock:
        logging_function(param1, param2, other_param="some text")
    assert _mock.call_count == 3
    assert "Calling method" in str(_mock.call_args_list[0].args[0])
    assert f"Params: ({param1}, {param2})" in str(_mock.call_args_list[0].args[0])
    assert "{'other_param': 'some text'}" in str(_mock.call_args_list[0].args[0])
    assert "Result" in str(_mock.call_args_list[1].args[0])
    assert f'logging_function": {param1 + param2}' in str(_mock.call_args_list[1].args[0])


def test_logging_when_wrong_argument():
    """test logging call function with wrong argument"""

    with patch("src.core.wrappers.log_msg") as _mock:
        try:
            # pylint: disable=no-value-for-parameter
            logging_function()
        except TypeError:
            pass

    assert _mock.call_count == 4
    assert "Calling method" in str(_mock.call_args_list[0].args[0])
    assert "logging_function" in str(_mock.call_args_list[0].args[0])
    assert "Label test_logging" in str(_mock.call_args_list[0].args[0])

    assert "Runtime error" in str(_mock.call_args_list[1].args[0])
    assert "missing 2 required positional arguments" in str(_mock.call_args_list[1].args[0])

    assert "Result" in str(_mock.call_args_list[2].args[0])
    assert ": None" in str(_mock.call_args_list[2].args[0])

    assert "End of call to method" in str(_mock.call_args_list[3].args[0])
    assert "[exec_period]" in str(_mock.call_args_list[3].args[0])
