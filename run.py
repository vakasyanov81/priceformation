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
from src.core.log_message import print_log
from src.parsers.all_vendors import all_vendors
from src.parsers.common_price import CommonPrice
from src.parsers.vendors.zapaska import load_data


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
        case AnswerResult.MAKE_PRICE_BY_SUPPLIER:
            await try_call(run_make_price_by_supplier)
        case AnswerResult.UPDATE_ZAPASKA_DATA:
            await try_call(run_upload_zapaska_data)
        case AnswerResult.EXIT:
            sys.exit(0)


def run_make_price_by_supplier():
    """Make common price list by price list supplier's"""
    common_price = CommonPrice()
    common_price.parse_all_vendors(all_vendors())
    common_price.write_all_prices()


def run_upload_zapaska_data():
    """Load zapaska data from api"""
    load_data()
    print_log("*** Данные успешно загружены. ***\n")


if __name__ == "__main__":
    asyncio.run(main())
