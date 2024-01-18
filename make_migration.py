# -*- coding: utf-8 -*-
"""
Инициализация базы данных
"""
__author__ = "Kasyanov V.A."

import asyncio
import traceback

from core.log_message import err_msg, print_log
from database.db import close_db
from database.exception import DBError
from database.init_db import init_db


async def make_migration():
    """
    entry point
    :return:
    """

    try:
        await init_db(drop_database=True)
    except KeyboardInterrupt:
        exit(0)
    except DBError as exc:
        print_log(str(exc), level="WARNING")
        exit(1)
    except Exception as exc:
        err_msg(str(exc))
        err_msg(traceback.format_exc())
        print_log(f"Не предвиденная ошибка // {str(exc)}", level="WARNING")
        exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(make_migration())
    finally:
        close_db()
