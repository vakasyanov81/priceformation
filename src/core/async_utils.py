"""Async help logic"""

import sys

from src.core.exceptions import SupplierNotHavePricesError
from src.core.log_message import print_log


async def try_call(method, _async=False, **kwargs):
    """Try method call"""
    try:
        if _async:
            await method(**kwargs)
        else:
            method(**kwargs)
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level="WARNING")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)
