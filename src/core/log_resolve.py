"""Resolve log level labels, paths and logging callables."""

import logging
from typing import Any, Callable

from core.log_paths import get_log_paths

__level_map__ = {
    logging.ERROR: "ERROR",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
}


def get_log_level_text(log_level: int) -> str:
    """Map logging level int to text label."""
    return __level_map__.get(log_level) or "INFO"


def resolve_log_path(level: int = logging.INFO) -> str:
    """get directory path for logging by log-level"""
    paths = get_log_paths()
    log_file_map = {logging.ERROR: paths.err_file}

    return log_file_map.get(level) or paths.log_file


def resolve_log_method(level: int = logging.INFO) -> Callable[..., Any]:
    """get logging method by log-level"""
    log_method_mapping = {
        logging.INFO: logging.info,
        logging.WARNING: logging.warning,
        logging.ERROR: logging.error,
    }

    return log_method_mapping.get(level) or logging.info
