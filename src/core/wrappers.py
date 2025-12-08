"""
logging decorators
"""

import logging as __logging
import time
import traceback
from typing import Callable, TypeVar

from .log_message import log_msg

CALL_BEGIN_MSG = 'Calling method "{method}".'
CALL_END_MSG = 'End of call to method "{method}" [exec_period] {period}'
CALL_LABEL_MSG = "\n\rLabel {label}"
CALL_PARAMS_MSG = "\n\rParams: {params}"
CALL_TRACE_MSG = 'Runtime error "{method}":\n\r{trace}'
CALL_RESULT_MSG = 'Result "{method}": {res}'


RT = TypeVar('RT')  # return type


def _decorator(func: Callable[..., RT], label: str = "") -> Callable[..., RT]:
    """log decorator"""

    def wrapped(*args, **kwargs) -> RT:  # type: ignore
        """wrapper for super method"""
        result = None
        method_name: str = func.__module__ + "." + func.__name__
        start_time = time.time()
        msg = CALL_BEGIN_MSG.format(method=method_name)

        if label:
            msg += CALL_LABEL_MSG.format(label=label)

        msg += CALL_PARAMS_MSG.format(params=str(args))
        if kwargs:
            msg += "\n" + str(kwargs)
        log_msg(msg)
        try:
            result = func(*args, **kwargs)
            return result
        except Exception:
            log_msg(
                CALL_TRACE_MSG.format(method=method_name, trace=traceback.format_exc()),
                level=__logging.WARNING,
            )
            raise
        finally:
            delta = int((time.time() - start_time) * 1000)
            log_msg(CALL_RESULT_MSG.format(method=method_name, res=repr(result)))
            log_msg(CALL_END_MSG.format(method=method_name, period=delta))

    return wrapped


def logging(label: str = "") -> Callable[..., Callable[..., RT]]:
    """
    Wrapper for logging function
    """

    def decorate(func: Callable[..., RT], _label: str = label) -> Callable[..., RT]:
        """wrapper for supper method"""
        return _decorator(func, label=_label)

    return decorate
