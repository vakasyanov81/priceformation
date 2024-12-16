"""
Точка входа пользовательского интерфейса.
1. разбор позиций всех активных поставщиков
2. Формирование прайсов (для внутреннего использования, для дрома и т.д.)
"""

__author__ = "Kasyanov V.A."

import asyncio
import sys

from run_dialog import AnswerResult, ask_action
from src.core.async_utils import try_call
from src.database.db import close_db
from src.database.init_db import init_db
from src.database.nomenclature import save_nomenclature_to_db
from src.parsers.all_vendors import all_vendors
from src.parsers.common_price import CommonPrice


async def main():
    """
    entry point
    :return:
    """
    while True:
        await response_processing()


async def response_processing():
    """Ask questions"""
    match ask_action():
        case AnswerResult.MAKE_DB_MIGRATION:
            await try_call(init_db, _async=True)
        case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
            await try_call(run_make_price_by_supplier)
        case AnswerResult.SAVE_PRICE_TO_DB:
            await try_call(run_save_nomenclature_to_db, _async=True)
        case AnswerResult.EXIT:
            sys.exit(0)


def run_make_price_by_supplier():
    """Make common price list by price list supplier's"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    common_price.write_all_prices()


async def run_save_nomenclature_to_db():
    """Save supplier price list to database with data processing"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    await save_nomenclature_to_db(common_price)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        close_db()
