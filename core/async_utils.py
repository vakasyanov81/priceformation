"""Async help logic"""

import sys
import traceback

from core import err_msg
from core.exceptions import SupplierNotHavePricesError
from core.log_message import print_log
from database.exception import DBError, NotProvidedDatabaseError


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
    except DBError as exc:
        print_log(str(exc), level="ERROR")
        sys.exit(1)
    except NotProvidedDatabaseError as exc:
        err_msg(str(exc))
        err_msg(traceback.format_exc())
        print_log(f"Непредвиденная ошибка // {str(exc)}", level="ERROR")
        sys.exit(1)
