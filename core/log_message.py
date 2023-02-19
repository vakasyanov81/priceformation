# -*- coding: utf-8 -*-
"""
logic logging process
"""
__author__ = "Kasyanov V.A."

import datetime
import logging
from typing import Literal

from colorama import init
from termcolor import colored

from cfg import init_cfg
from core.init_log import init_log

cfg = init_cfg()
init()

__level_map__ = {
    logging.ERROR: "ERROR",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING"
}

__level_reverse_map__ = {
    "ERROR": logging.ERROR,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING
}


def err_msg(msg, need_print_log=False):
    """ make error message """
    return log_msg(msg, level=logging.ERROR, need_print_log=need_print_log)


def warn_msg(msg, need_print_log=False):
    """ make warning message """
    return log_msg(msg, level=logging.WARNING, need_print_log=need_print_log)


def resolve_log_path(level=logging.INFO):
    """ get directory path for logging by log-level """
    log_file_map = {
        logging.ERROR: cfg.main.current_err_log_file_path
    }

    return log_file_map.get(level) or cfg.main.current_log_file_path


def resolve_log_method(level=logging.INFO):
    """ get logging method by log-level """
    log_method_mapping = {
        logging.INFO: logging.info,
        logging.WARNING: logging.warning,
        logging.ERROR: logging.error
    }

    return log_method_mapping.get(level)


def log_to_file(msg, level=logging.INFO):
    """ make log to file """
    init_log()

    logging.basicConfig(
        filename=resolve_log_path(level),
        level=level
    )

    resolve_log_method(level)(msg)

    return True


def log_msg(msg, level=logging.INFO, need_print_log=False):
    """ make log message """

    time_now = datetime.datetime.time(datetime.datetime.now())
    if level == logging.ERROR:
        msg = f"[{time_now}] - {msg}"

    if not cfg.main.is_unittest_mode:
        log_to_file(msg, level=level)

    if need_print_log and not cfg.main.is_unittest_mode:
        print_log(msg, __level_map__.get(level))
    return True


def print_log(
        msg,
        level: Literal["INFO"] | Literal["ERROR"] | Literal["WARNING"] | None = "INFO",
        _color: Literal["red"] = "red"
):
    """ print log-message """

    # in unit test mode we hide the input of errors on the screen
    if cfg.main.is_unittest_mode and level != logging.INFO:
        return

    level_num = __level_reverse_map__.get(level)
    if level_num != logging.INFO:
        msg = f"[{level}]: {msg}"
        msg = colored(msg, _color)
