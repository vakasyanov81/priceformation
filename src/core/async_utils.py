"""Async help logic"""

import sys

from core.exceptions import SupplierNotHavePricesError
from core.log_message import print_log


def try_call(method, **kwargs):
    """Try method call"""
    try:
        method(**kwargs)
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level=logging.WARNING)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
