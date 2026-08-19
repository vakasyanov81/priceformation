"""
logic logging process
"""

import datetime
import logging
from typing import Literal

from colorama import init
from termcolor import colored

from core.init_log import init_log
from core.log_paths import get_log_paths
from core.log_resolve import get_log_level_text, resolve_log_method, resolve_log_path

init()

__level_color_map__ = {"ERROR": "red", "WARNING": "yellow", "Info": None}


def err_msg(message: str, need_print_log: bool = False) -> str:
    """make error message"""
    return log_msg(message, level=logging.ERROR, need_print_log=need_print_log)


def warn_msg(message: str, need_print_log: bool = False) -> str:
    """make warning message"""
    return log_msg(message, level=logging.WARNING, need_print_log=need_print_log)


def log_to_file(message: str, level: int = logging.INFO) -> bool:
    """make log to file"""
    init_log(get_log_paths().folder)
    logging.basicConfig(filename=resolve_log_path(level), level=level)
    resolve_log_method(level)(message)
    return True


def log_msg(
    msg: str,
    level: int = logging.INFO,
    need_print_log: bool = False,
    color: Literal["red", "green", "yellow"] | None = None,
) -> str:
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
) -> None:
    """print log-message"""

    level_title = get_log_level_text(level)
    formatted_msg = msg if level == logging.INFO else f"[{level_title}]: {msg}"
    print(colored(formatted_msg, _color or __level_color_map__.get(level_title)))
