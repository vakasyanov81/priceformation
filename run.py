# -*- coding: utf-8 -*-
"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
"""
__author__ = "Kasyanov V.A."

import asyncio
import dataclasses
import sys
from enum import Enum

from core.async_utils import try_async_call
from core.log_message import print_log
from database import save_nomenclature_to_db
from database.db import close_db
from database.init_db import init_db
from parsers.common_price import CommonPrice


@dataclasses.dataclass
class Colors:
    """Color scheme"""

    HEADER = "\033[95m"
    OK_BLUE = "\033[94m"
    OK_CYAN = "\033[96m"
    OK_GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    END_COLOR = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class AnswerResult(Enum):
    """Main actions"""

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
    """Main console menu"""
    _msg = (
        f"{Colors.BOLD}1 — миграция базы данных \n"
        "2 — сформировать общий прайс по прайсам поставщиков \n"
        "3 — записать номенклатуру поставщика в базу данных \n"
        f"q — выход {Colors.END_COLOR}"
    )
    while True:
        _answer = AnswerMap.get(input(_msg).strip().lower())
        if _answer:
            return _answer
        print_log("Не понял, давай ещё раз. \n")


async def main():
    """
    entry point
    :return:
    """
    while True:
        match ask_action():
            case AnswerResult.MAKE_DB_MIGRATION:
                await try_async_call(init_db, _async=True)
            case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
                await try_async_call(run_make_price_by_supplier)
            case AnswerResult.SAVE_PRICE_TO_DB:
                await try_async_call(run_save_nomenclature_to_db, _async=True)
            case AnswerResult.EXIT:
                sys.exit(0)


def run_make_price_by_supplier():
    """ Make common price list by price list supplier's """
    common_price = CommonPrice()
    common_price.parse_all_vendors()
    common_price.write_all_prices()


async def run_save_nomenclature_to_db():
    """ Save supplier price list to database with data processing """
    common_price = CommonPrice()
    common_price.parse_all_vendors()
    await save_nomenclature_to_db(common_price)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        close_db()
