import traceback

from core import err_msg
from core.exceptions import SupplierNotHavePricesError
from core.log_message import print_log
from database.exception import DBError


async def try_async_call(method, _async=False, **kwargs):
    try:
        if _async:
            await method(**kwargs)
        else:
            method(**kwargs)
    except SupplierNotHavePricesError as exc:
        print_log(f"{exc}", level="WARNING")
        exit(1)
    except KeyboardInterrupt:
        exit(0)
    except DBError as exc:
        print_log(str(exc), level="ERROR")
        exit(1)
    except Exception as exc:
        err_msg(str(exc))
        err_msg(traceback.format_exc())
        print_log(f"Непредвиденная ошибка // {str(exc)}", level="ERROR")
        exit(1)
