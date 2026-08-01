"""Async help logic"""

import logging
import sys
from typing import Any, Callable

from core.exceptions import SupplierNotHavePricesError
from core.log_message import print_log


def try_call(method: Callable[..., Any], **kwargs: Any) -> None:
    """Try method call"""
    try:
        method(**kwargs)
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level=logging.WARNING)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
