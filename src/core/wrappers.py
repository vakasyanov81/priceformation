"""
logging decorators
"""

import logging as _logging_module
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


RT = TypeVar("RT")  # return type


def _build_begin_msg(method_name: str, label: str, args, kwargs) -> str:
    """Собрать сообщение о старте вызова."""
    msg = CALL_BEGIN_MSG.format(method=method_name)
    if label:
        msg += CALL_LABEL_MSG.format(label=label)
    msg += CALL_PARAMS_MSG.format(params=str(args))
    if kwargs:
        msg = "".join((msg, f"\n{kwargs}"))
    return msg


def _log_call_end(method_name: str, start_time: float, call_output) -> None:
    """Лог результата и длительности вызова."""
    delta = int((time.time() - start_time) * 1000)
    log_msg(CALL_RESULT_MSG.format(method=method_name, res=repr(call_output)))
    log_msg(CALL_END_MSG.format(method=method_name, period=delta))


def _log_trace(method_name: str) -> None:
    """Лог traceback при ошибке."""
    log_msg(
        CALL_TRACE_MSG.format(method=method_name, trace=traceback.format_exc()),
        level=_logging_module.WARNING,
    )


def _decorator(func: Callable[..., RT], label: str = "") -> Callable[..., RT]:
    """log decorator"""

    def wrapped(*args, **kwargs) -> RT:  # type: ignore
        """wrapper for super method"""
        call_output = None
        method_name = f"{func.__module__}.{func.__name__}"
        start_time = time.time()
        log_msg(_build_begin_msg(method_name, label, args, kwargs))
        try:
            call_output = func(*args, **kwargs)
        except Exception:
            _log_trace(method_name)
            raise
        finally:
            _log_call_end(method_name, start_time, call_output)
        return call_output

    return wrapped


def logging(label: str = "") -> Callable[..., Callable[..., RT]]:
    """
    Wrapper for logging function
    """

    def decorate(func: Callable[..., RT], _label: str = label) -> Callable[..., RT]:
        """wrapper for supper method"""
        return _decorator(func, label=_label)

    return decorate
