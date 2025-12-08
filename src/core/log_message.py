"""
logic logging process
"""

import datetime
import logging
from typing import Callable, Literal

from colorama import init
from termcolor import colored

from cfg import init_cfg
from core.init_log import init_log

cfg = init_cfg()
init()

__level_map__ = {
    logging.ERROR: "ERROR",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
}


def get_log_level_text(log_level: int) -> str:
    return __level_map__.get(log_level) or "INFO"


__level_reverse_map__ = {
    "ERROR": logging.ERROR,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
}

__level_color_map__ = {"ERROR": "red", "WARNING": "yellow", "Info": None}


def err_msg(message: str, need_print_log: bool = False) -> str:
    """make error message"""
    return log_msg(message, level=logging.ERROR, need_print_log=need_print_log)


def warn_msg(message: str, need_print_log: bool = False):
    """make warning message"""
    return log_msg(message, level=logging.WARNING, need_print_log=need_print_log)


def resolve_log_path(level=logging.INFO):
    """get directory path for logging by log-level"""
    log_file_map = {logging.ERROR: cfg.main.current_err_log_file_path}

    return log_file_map.get(level) or cfg.main.current_log_file_path


def resolve_log_method(level=logging.INFO) -> Callable:
    """get logging method by log-level"""
    log_method_mapping = {
        logging.INFO: logging.info,
        logging.WARNING: logging.warning,
        logging.ERROR: logging.error,
    }

    return log_method_mapping.get(level) or logging.info


def log_to_file(message: str, level=logging.INFO) -> bool:
    """make log to file"""
    init_log()

    logging.basicConfig(filename=resolve_log_path(level), level=level)

    resolve_log_method(level)(message)

    return True


def log_msg(
    msg: str,
    level: int = logging.INFO,
    need_print_log: bool = False,
    color: Literal["red", "green", "yellow"] | None = None,
):
    """make log message"""

    time_now = datetime.datetime.time(datetime.datetime.now())
    if level == logging.ERROR:
        msg = f"[{time_now}] - {msg}"

    if level == logging.ERROR:
        log_to_file(msg, level=level)

    if need_print_log:
        print_log(msg, level, _color=color)
    return msg


def print_log(
    msg: str,
    level: int = logging.INFO,
    _color: Literal["red", "green", "yellow"] | None = None,
):
    """print log-message"""

    _msg = ""
    level_title = get_log_level_text(level)
    if level != logging.INFO:
        _msg = f"[{level_title}]: "
    _msg += f"{msg}"
    _msg = colored(_msg, _color or __level_color_map__.get(level_title))
    print(_msg)
