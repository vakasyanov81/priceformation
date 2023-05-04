# -*- coding: utf-8 -*-
"""
точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
"""
__author__ = "Kasyanov V.A."

import asyncio
import traceback
from enum import Enum

from core.log_message import err_msg, print_log
from database import save_nomenclature_to_db
from database.db import close_db
from database.exception import DBError
from database.init_db import init_db
from database.supplier import get_statistic
from parsers.base_parser.base_parser import SupplierNotHavePricesError
from parsers.common_price import CommonPrice


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


MAKE_PRICE_BY_SUPPLIER = "MakePriceBySupplier"


class AnswerResult(Enum):
    MAKE_DB_MIGRATION = "MakeDBMigration"
    MAKE_PRICE_BY_SUPPLIER = "MakePriceBySupplier"
    SAVE_PRICE_TO_DB = "SavePriceToDB"
    EXIT = "Exit"


AnswerMap = {
    "1": AnswerResult.MAKE_DB_MIGRATION,
    "2": AnswerResult.MAKE_PRICE_BY_SUPPLIER,
    "3": AnswerResult.SAVE_PRICE_TO_DB,
    "q": AnswerResult.EXIT,
}


def ask_action() -> AnswerResult:
    _msg = (
        f"{Colors.HEADER}1 — миграция базы данных, \n"
        "2 — сформировать общий прайс по прайсам поставщиков, \n"
        "3 — актуализация базы данных, \n"
        f"q — выход: {Colors.ENDC}"
    )
    while True:
        _answer = AnswerMap.get(input(_msg).strip().lower())
        if _answer:
            return _answer
        else:
            print_log("Не понял, давай ещё раз. \n")


async def main():
    """
    entry point
    :return:
    """
    print(await get_statistic())
    while True:
        match ask_action():
            case AnswerResult.MAKE_DB_MIGRATION:
                await _try(init_db, _async=True)
            case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
                await _try(run_make_price_by_supplier)
            case AnswerResult.SAVE_PRICE_TO_DB:
                await _try(run_save_nomenclature_to_db, _async=True)
            case AnswerResult.EXIT:
                exit(0)


async def _try(method, _async=False, **kwargs):
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
        print_log(str(exc), level="WARNING")
        exit(1)
    except Exception as exc:
        err_msg(str(exc))
        err_msg(traceback.format_exc())
        print_log(f"Непредвиденная ошибка // {str(exc)}", level="WARNING")
        exit(1)


def run_make_price_by_supplier():
    common_price = CommonPrice()
    common_price.parse_all_vendors()
    common_price.write_all_prices()


async def run_save_nomenclature_to_db():
    common_price = CommonPrice()
    common_price.parse_all_vendors()
    await save_nomenclature_to_db(common_price)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        close_db()
