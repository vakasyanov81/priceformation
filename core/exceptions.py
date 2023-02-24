# -*- coding: utf-8 -*-
"""
raise logic
"""
__author__ = "Kasyanov V.A."

import traceback

from .log_message import err_msg

__STACK_TRACE_LIMIT__ = 10


class CoreExceptionError(Exception):
    """Wrapper on Exception. This logic for logging exception"""

    __MESSAGE__ = None

    def __init__(self, msg=None):
        msg = msg or self.__MESSAGE__
        self.to_log(msg)
        super().__init__(msg)

    @classmethod
    def to_log(cls, msg):
        """log message with trace"""
        trace_message = str(traceback.extract_stack(limit=__STACK_TRACE_LIMIT__))
        trace_message = f"{msg} \n {trace_message}"
        err_msg(trace_message)


def make_raise(message):
    """prepare message for raise, logging raise message"""
    raise CoreExceptionError(message)


__ALL__ = [make_raise]
