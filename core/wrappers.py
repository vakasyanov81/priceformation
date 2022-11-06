# -*- coding: utf-8 -*-
"""
logging decorators
"""
__author__ = "Kasyanov V.A."

import time
import traceback
import logging as __logging
from .log_message import log_msg

CALL_BEGIN_MSG = "Calling method \"{method}\"."
CALL_END_MSG = "End of call to method \"{method}\" [exec_period] {period}"
CALL_LABEL_MSG = "\n\rLabel {label}"
CALL_PARAMS_MSG = "\n\rParams: {params}"
CALL_TRACE_MSG = "Runtime error \"{method}\":\n\r{trace}"
CALL_RESULT_MSG = "Result \"{method}\": {res}"


def _decorator(func, label=""):
    """ log decorator """
    def wrapped(*args, **kwargs):
        """ wrapper for super method """
        result = None
        method = func.__module__ + "." + func.__name__
        start_time = time.time()
        msg = CALL_BEGIN_MSG.format(method=method)

        if label:
            msg += CALL_LABEL_MSG.format(label=label)

        msg += CALL_PARAMS_MSG.format(params=str(args))
        if kwargs:
            msg += "\n" + str(kwargs)
        log_msg(msg)
        try:
            result = func(*args, **kwargs)
        except Exception:
            log_msg(
                CALL_TRACE_MSG.format(
                    method=method,
                    trace=traceback.format_exc()
                ),
                level=__logging.WARNING
            )
            raise
        finally:
            delta = int((time.time() - start_time) * 1000)
            log_msg(CALL_RESULT_MSG.format(method=method, res=repr(result)))
            log_msg(CALL_END_MSG.format(method=method, period=delta))
        return result

    return wrapped


def logging(label=""):
    """
    Wrapper for logging function
    """

    def decorate(func, _label=label):
        """ wrapper for supper method """
        return _decorator(func=func, label=_label)

    return decorate
