"""
raise logic
"""

import logging
import traceback

from core.log_message import err_msg

__STACK_TRACE_LIMIT__ = 10


class CoreExceptionError(Exception):
    """Wrapper on Exception. This logic for logging exception"""

    __MESSAGE__: str | None = None

    def __init__(self, msg: str | None = None, *, detail: str | None = None) -> None:
        msg = msg or self.__MESSAGE__
        self.to_log(detail or msg)
        super().__init__(msg)

    @classmethod
    def to_log(cls, msg: str | None) -> None:
        """Write message and stack to the error log file, not to the console."""
        trace_message = str(traceback.extract_stack(limit=__STACK_TRACE_LIMIT__))
        trace_message = f"{msg} \n {trace_message}"
        try:
            err_msg(trace_message, need_print_log=False)
        except (RuntimeError, OSError):
            logging.error(trace_message)


def make_raise(message: str) -> None:
    """prepare message for raise, logging raise message"""
    raise CoreExceptionError(message)


__ALL__ = [make_raise]


class SupplierNotHavePricesError(CoreExceptionError):
    """Raise in case supplier have not price"""
