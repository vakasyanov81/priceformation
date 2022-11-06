# -*- coding: utf-8 -*-
"""
log, raise interfaces
"""
__author__ = "Kasyanov V.A."

from .log_message import (
    log_msg,
    err_msg,
    warn_msg
)

from .exceptions import make_raise, CoreException

__ALL_ = [log_msg, err_msg, warn_msg, make_raise, CoreException]
