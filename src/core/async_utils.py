"""Async help logic"""

import logging
import sys
from collections.abc import Callable
from typing import Any

from core.exceptions import CoreExceptionError, SupplierNotHavePricesError
from core.log_message import print_log


def try_call(method: Callable[..., Any], **kwargs: Any) -> None:
    """Try method call"""
    try:
        method(**kwargs)
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level=logging.WARNING)
        sys.exit(1)
    except CoreExceptionError as exc:
        print_log(f"{exc}", level=logging.ERROR)
    except KeyboardInterrupt:
        sys.exit(0)
